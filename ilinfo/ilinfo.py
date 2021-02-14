# Created by Andre Machon 07/02/2021

import json
import logging
import os
import re
import subprocess
import click
from copy import deepcopy
from json import dumps
from os import path as osp

from ilinfo.utils import find_files_recursive, parse_ini_file
from ilinfo.mixins import PermissionMixin, PermissionException

INI_MAPPING = {
    "ilias.ini.php": {
        "server": ['http_path', 'absolute_path'],
        "clients": ['path', 'inifile', 'datadir', 'default']
    },
    "client.ini.php": {
        "client": ['name', 'access'],
        "db": ['type', 'host', 'user', 'name', 'pass', 'port'],
        'language': ['default'],
        'layout': ['skin', 'style']
    },
}

EXCLUDED_FOLDERS = [
    'Backup', 'backup', '_Examples', 'Dump', 'dump', 'iliasold', 'ilias5_old', 'ilias4_old', 'defekt',
    'ilias5old', 'ilias4old', 'iliasOld', 'iliasold', 'ilias4svn', 'ilias5svn',
    '/opt', '/root', '/etc', '/media', '/mnt', '/lib', '/sbin', '/tmp'
]


@click.group()
def analyze():
    pass


@analyze.command()
def ilias():
    pass


@analyze.command()
def system():
    pass


class IliasInfo(PermissionMixin):
    """Get information about ILIAS installations under a specified path

    """
    data = {}
    il_install_paths = []
    exclude_dirs = []
    current_il_path = None

    def __init__(self, options, *args, **kwargs):
        self.log = logging.getLogger('{}.{}'.format(self.__module__, self.__class__.__name__))
        level = int(kwargs.get('log_level', 20))
        self.log.setLevel(level)
        self.log.debug('Permission level is: %s', self.PERMISSION_LEVEL)

    def run(self):
        """ Main CLI Method: Recursively traverses a directory tree to identify and analyze ILIAS installations

        :return:
        """
        # print('You supplied the following options:', dumps(self.options, indent=2, sort_keys=True))
        # print('Log Level: ', self.get_level_name(self.log.level))

        for install_path in self._find_il_paths(self.options['<path>']): # TODO replace options with click parameter
            print('Identified the following path as ILIAS root: ', install_path)
            self.log.debug('Identified the following path as ILIAS root: %s', install_path)
            self.il_install_paths.append(install_path)

        for search_path in self.il_install_paths:
            plugins = {}
            print('Analyzing installation in: ', search_path)
            self.log.debug('Analyzing installation in: %s', search_path)
            if search_path:
                pa, version = self._find_il_version(search_path)

                for p, plugin_name, data in self._parse_il_plugins(search_path):
                    if not p or not plugin_name:
                        continue
                    plugins.update({plugin_name: data})

                try:
                    remotes_dict = self.format_git_remote_to_dict(self.get_git_remote_info(search_path))
                except (AttributeError, KeyError, ValueError):
                    remotes_dict = {}

                try:
                    recursive_remotes = {}
                    for repo_dir, remote_dict in self.get_git_remote_info_recursive(search_path):
                        recursive_remotes[repo_dir] = remote_dict
                except (AttributeError, KeyError, ValueError) as err:
                    self.log.error("Error while finding out all contained git remotes in path: ", search_path, err)
                    recursive_remotes = {}

                self.data[search_path] = {
                    'ilias_version': version.groups()[0],
                    'git_remotes': remotes_dict,
                    'contained_repositories': recursive_remotes,
                    'clients': {},
                    # TODO see if this method works without errors and can be reenabled
                    # 'skins': self._parse_il_skins(search_path),
                    'plugins': plugins
                }

        self._parse_il_ini_files(self.default_mapping.items())
        self._find_active_plugins()

        # save results to cache file, that base command class loads on program excecution
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '.iliasinfo.json'), 'w') as cache_file:
            json.dump(self.data, cache_file)
        # save to user specified file
        if self.options['--to_json']:
            with open(self.options['--to_json'], 'w') as jsonfile:
                json.dump(self.data, jsonfile, indent=2)
            return 'All data was gathered and saved to {}'.format(jsonfile.name)
        return self.data

    def analyze_installation(self, ilias_path):
        plugins = {}
        search_path, ilias_version = self._find_il_version(ilias_path)

        # parse plugins
        for p, plugin_name, data in self._parse_il_plugins(search_path):
            if not p or not plugin_name:
                continue
            plugins.update({plugin_name: data})

        try:
            remotes_dict = self.format_git_remote_to_dict(self.get_git_remote_info(search_path))
        except (AttributeError, KeyError, ValueError):
            remotes_dict = {}

        try:
            recursive_remotes = {}
            for repo_dir, remote_dict in self.get_git_remote_info_recursive(search_path):
                recursive_remotes[repo_dir] = remote_dict
        except (AttributeError, KeyError, ValueError) as err:
            self.log.error("Error while finding out all contained git remotes in path: ", search_path, err)
            recursive_remotes = {}

        # build data for JSON file
        self.data[search_path] = {
            'ilias_version': ilias_version.groups()[0],
            'git_remotes': remotes_dict,
            'contained_repositories': recursive_remotes,
            'clients': {},
            # 'skins': self._parse_il_skins(search_path),
            'plugins': plugins
        }

    @staticmethod
    def parse_il_plugin_php(filename, encoding='utf-8'):
        d = {}
        with open(filename, encoding=encoding) as plugin_php:
            for i, line in enumerate(plugin_php):
                if i == 0:
                    continue
                result_php_var = re.search(r"\$(\w+)\s+?=\s+?[\"']([a-zA-Z\@\s\.]+|[0-9\.]+)[\"'];", line)
                result_define = re.search(r"define\(['\"]([a-zA-Z_]+)['\"],\s?['\"]([0-9\.]+)['\"]\);", line)
                if result_php_var:
                    d[result_php_var.groups()[0]] = result_php_var.groups()[1]
                if result_define:
                    d[result_define.groups()[0]] = result_define.groups()[1]
        return d

    @staticmethod
    def get_git_remote_info_recursive(root_path):
        for repo_dir in IliasInfo.find_contained_repositories(root_path):
            yield repo_dir, IliasInfo.format_git_remote_to_dict(IliasInfo.get_git_remote_info(repo_dir))

    @staticmethod
    def find_contained_repositories(root_path):
        repository_paths = []
        for current_path, dirs, files in os.walk(root_path):
            if ".git" in dirs:
                repository_paths.append(current_path)

        return repository_paths

    @staticmethod
    def get_git_remote_info(remote_path):
        try:
            if "run" in dir(subprocess):
                # CalledProcessError
                cp = subprocess.run(['git', 'remote', '-v'], cwd=remote_path, stdout=subprocess.PIPE)
                return cp.stdout.decode('utf8')
            else:
                cp = subprocess.check_output(['git', 'remote', '-v'], cwd=remote_path)
                return str(cp, 'utf-8')
        except subprocess.CalledProcessError as err:
            print(err)
            return ""

    @staticmethod
    def format_git_remote_to_dict(remote_str):
        lines = remote_str.splitlines()
        formatted_lines = [tuple(l.split(' ')[0].split('\t')) for l in lines]
        remote_dict = {}
        for l in formatted_lines:
            remote_dict.update({l[0]: l[1]})

        return remote_dict

    def _parse_il_ini_files(self, config):
        """ Searches for ilias.ini.php and client.ini files within path from config object and gathers data from them

        :param config: dictionary with mapping, of which ini sections and values to save
        :type config: dict_items
        :rtype: dict
        :return: dictionary which holds complete data structure for all ILIAS installations found by calling iliasinfo
        """

        for filename, parse_config in config:
            for ini_file in find_files_recursive(self.options['<path>'], filename, self.exclude_dirs):
                self._match_to_il_path(ini_file)

                if not self.current_il_path:
                    continue

                if filename == 'ilias.ini.php':
                    d = parse_ini_file(ini_file, parse_config=parse_config)
                    self.data[self.current_il_path]['ilias_ini'] = d
                    self.log.debug('Parsed .ini file %s, got data: %s', ini_file, d)

                if 'client.ini' in filename:
                    d = {'client_ini': parse_ini_file(ini_file, parse_config=parse_config)}
                    self.data[self.current_il_path]['clients'][os.path.basename(os.path.dirname(ini_file))] = d
                    self.log.debug('Parsed .ini file %s, got data: %s', ini_file, d)

        return self.data

    def _parse_il_skins(self, ilias_path):
        """ Parses all skins within an ILIAS installation and returns dictionary with found data

        :param ilias_path: Path of ILIAS installation
        :type ilias_path: str
        :return: skin info dictionary
        :rtype: dict
        """

        skins = {}
        try:
            # go to Customizing/skins
            for i, (root, dirs, files) in enumerate(os.walk(os.path.join(ilias_path, 'Customizing/global/skin'))):
                if i > 0:
                    break

                for skin_dir in dirs:
                    self.log.debug('Searching for skins in: %s', os.path.join(root, skin_dir))

                    name, skin_data = self._parse_skin(os.path.join(root, skin_dir))
                    skins[name] = skin_data
            self.log.debug('Found the following skins: %s', skins)
            return skins

        except NotADirectoryError as err:
            print(err)
            self.log.error(err)

    def _parse_skin(self, skin_path):
        """ Parses a single skin folder to get ID, name, substyle names, skin version, ILIAS version

        :param skin_path: Full path to the skin folder
        :type skin_path: str
        :return: tuple of skin name and dictionary with information about the skin
        :rtype: tuple
        """

        d = {}
        try:
            with open(os.path.join(skin_path, 'template.xml'), 'r') as tp_file:
                txt = tp_file.read()
                skin_version = re.search(r'version {0,1}= {0,1}\"([0-9]+)\"', txt)
                ilias_version = re.search(r'\" name {0,1}\= {0,1}\"((\w|\d|\.|-| )+)\"', txt)
                substyle_names = re.findall(r'((substyle) name {0,1}\= {0,1}\"((\w|\d|\.|-| )+)\")', txt)
                ids = re.findall(r'id {0,1}\= {0,1}\"((\w|\d|\.|-| )+)\"', txt)

                # d['skin_name'] = os.path.basename(skin_path)

                if skin_version:
                    d['skin_version'] = skin_version.group(1)
                if ilias_version:
                    d['ilias_version'] = ilias_version.group(1)
                if ids:
                    d['skin_id'] = ids.pop(0)[0]

                if substyle_names:
                    sub_names = [grps[2] for grps in substyle_names]
                if ids:
                    ids = [grps[0] for grps in ids]
                    if substyle_names:
                        sub_names_ids = [{'name': name, 'id': sID} for name, sID in list(zip(sub_names, ids))]
                        d['substyles'] = sub_names_ids
            return os.path.basename(skin_path), d

        except (FileNotFoundError, FileExistsError, PermissionError) as err:
            print(err)

    def _parse_il_plugins(self, search_path):
        """Finds and Analyzes all Plugins in an ILIAS installation

        :param search_path: Full path to the ILIAS installation
        :type search_path: str
        :return: yields a tuple of the ILIAS path, plugin name and dictionary containing information about the plugin
        :rtype: tuple
        """

        # self.log.debug('Analyzing Plugins in path: %s', search_path)
        for plugin_php in self._find_il_plugins(search_path):
            if not plugin_php:
                continue
            try:
                d = self.parse_il_plugin_php(plugin_php)
            except UnicodeDecodeError as err:
                d = self.parse_il_plugin_php(plugin_php, encoding='ISO-8859-1')

            try:
                fpath = os.path.join(os.path.dirname(plugin_php), 'classes')
                plugin_classes = [f for f in os.listdir(fpath) if os.path.isfile(os.path.join(fpath, f))]

                for f in plugin_classes:
                    result = re.search(r"class\.il(\w+)Plugin\.php", f)
                    if result:
                        plugin_name = result.groups()[0]
                    else:
                        continue

                self._match_to_il_path(fpath)
                ilias_path = self.current_il_path

                # self.log.debug('Found Plugin %s in path: %s with plugin.php info: %s', plugin_name, ilias_path, d)
                yield ilias_path, plugin_name, d
            except (FileNotFoundError, FileExistsError) as err:
                print('Unable to parse plugin from plugin.php: ', plugin_php)
                print(err)
                # self.log.error('Unable to parse plugin from plugin.php: %s', err)
                continue

    def _find_il_paths(self, search_path):
        """Recursively searches a path for all ILIAS installations

        Any path containing a value that is in self.exclude_dirs, is skipped. This happens to account for backups,
        Skip irrelevant paths to speed up execution and enable us to customize which installations should be skipped

        :param search_path: Path to start searching from. In most cases "/" is the best option
        :type search_path: str
        :return: yields full path to each found ILIAS installation
        :rtype: str
        """

        exclude_dirs = deepcopy(self.exclude_dirs)
        exclude_dirs.append('Customizing/global')
        for file in find_files_recursive(search_path, 'ilias.php', exclude_dirs):
            yield os.path.dirname(file)

    def _match_to_il_path(self, search_path):
        """Recursive function that tries to match a path to a found ILIAS path

        This happens by removing the last element and trying for a match again until one is found or no element is left.
        This Function has a strange bug, where returning does not work, even though we have a value (Python core bug)

        :param search_path: Any path other than "/"
        :type search_path: str
        :return: None
        :rtype: NoneType
        """

        if search_path == '/':
            return

        self.current_il_path = None
        p = os.path.dirname(search_path)

        if search_path in self.il_install_paths:
            self.current_il_path = search_path
        if p in self.il_install_paths:
            self.current_il_path = p
        else:
            self._match_to_il_path(p)

    def _find_il_version(self, search_path, filename='inc.ilias_version.php'):
        for file in find_files_recursive(search_path, filename, self.exclude_dirs):
            version = re.search(r"\"(\d\.\d\.\d+)\"", open(file).read())
            return search_path, version

    def _find_il_plugins(self, search_path, filename='plugin.php'):
        for file in find_files_recursive(search_path, filename, self.exclude_dirs):
            yield file


if __name__ == '__main__':
    analyze()
