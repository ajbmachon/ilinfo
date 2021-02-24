# Created by Andre Machon 14/02/2021
import re
import subprocess
from os import path as osp
from pathlib import Path
from copy import deepcopy

from ilinfo.utils import parse_ini_to_dict, find_files_recursive
from ilinfo.output_processors import OutputProcessor, JSONOutput

__all__ = ['IliasAnalyzer', 'IliasFileParser', 'IliasPathFinder', 'GitHelper']


class IliasAnalyzer:
    """Aggregates the IliasFileParser, IliasPathFinder and GitHelper to analyze the systems ILIAS installations"""

    def __init__(self, fileparser=None, pathfinder=None, git_helper=None, output_processor=None, excluded_folders=None):
        self._data = {}
        self._check_init_params(fileparser, pathfinder, git_helper, output_processor)

        self._file_parser = fileparser or IliasFileParser()
        self._pathfinder = pathfinder or IliasPathFinder()
        self._git_helper = git_helper or GitHelper()
        self._output_processor = output_processor or JSONOutput()
        self._excluded_folders = excluded_folders

    def _check_init_params(self, fileparser=None, pathfinder=None, git_helper=None, output_processor=None, excluded_folders=None):
        if fileparser is not None:
            if not isinstance(fileparser, IliasFileParser):
                raise TypeError('Param fileparser needs to be of type IliasFileParser, or None')
        if pathfinder is not None:
            if not isinstance(pathfinder, IliasPathFinder):
                raise TypeError('Param pathfinder needs to be of type IliasPathFinder, or None')
        if git_helper is not None:
            if not isinstance(git_helper, GitHelper):
                raise TypeError('Param git_helper needs to be of type GitHelper, or None')
        if output_processor is not None:
            if not issubclass(output_processor, OutputProcessor):
                raise TypeError('Param output_processor needs to be a subclass of OutputProcessor, or None')
        if excluded_folders is not None:
            if not isinstance(excluded_folders, dict):
                raise TypeError('Param excluded_folders needs to be of type dict, or None')

    def analyze_path(self, start_path):
        # analyze path recursively with iliaspathfinder
        # self._pathfinder.find_installations(start_path, self._excluded_folders)
        # self._pathfinder.find_plugins(start_path, self._excluded_folders)

        # for each installation found parse files via iliasfileparser and

        # output results via output processor
        pass


class IliasFileParser:
    """Parses ILIAS files into dictionaries

    PARSABLE FILES:
        ilias.ini.php
        client.ini.php
        inc.ilias_version.php
        plugin.php

    """

    def __init__(self):
        self._data = {}
        self._current_installation = {
            'ilias_path': '',
            'client.ini.php': [],
            'plugin.php': []
        }
        self._git_helper = GitHelper()

    __slots__ = ['_data', '_git_helper', '_current_installation']

    @property
    def data(self):
        self._append_current_installation_to_data()
        return deepcopy(self._data)

    def _append_current_installation_to_data(self):
        ilias_path = self._current_installation.get('ilias_path', None)
        if ilias_path and ilias_path not in self._data:
            self._data[ilias_path] = self._current_installation
            self._current_installation = {
                'ilias_path': '',
                'client.ini.php': [],
                'plugin.php': []
            }

    def parse_from_pathfinder(self, pathfinder):
        if not isinstance(pathfinder, IliasPathFinder):
            raise TypeError("Param pathfinder needs to be of class IliasPathFinder")

        for ilias_path, ilias_dict in pathfinder:
            self._current_installation['ilias_path'] = ilias_path
            ilias_files = ilias_dict.get('files', {})

            self.parse_ilias_ini(ilias_files.get('ilias.ini.php'))
            self.parse_gitmodules(ilias_files.get('.gitmodules'))

            for client_ini in ilias_files.get('client.ini.php'):
                self.parse_client_ini(client_ini)
            for pl_name, pl_php_path in ilias_dict.get('plugins').items():
                # get dirname as parse_plugin does not expect full path to plugin.php
                self.parse_plugin(osp.dirname(pl_php_path))

            self._append_current_installation_to_data()

        return self.data

    def parse_ilias_ini(self, file_path):
        """Parses ilias.ini.php file for information about ILIAS installation

        :param file_path: path to ilias.ini.php file
        :type file_path: str
        :return: dict with client and path information
        :rtype: dict
        """
        d = parse_ini_to_dict(file_path, {
            "server": ['http_path', 'absolute_path'],
            "clients": ['path', 'inifile', 'datadir', 'default']
        })
        self._current_installation['ilias.ini.php'] = d
        return d

    def parse_client_ini(self, file_path):
        """Parses client.ini.php file for information about skins, language and db connections

        :param file_path: path to client.ini.php file
        :type file_path: str
        :return: dict with db connection and further client specific information
        :rtype: dict
        """
        d = parse_ini_to_dict(file_path, {
            "client": ['name', 'access'],
            "db": ['type', 'host', 'user', 'name', 'pass', 'port'],
            'language': ['default'],
            'layout': ['skin', 'style']
        })
        self._current_installation['client.ini.php'].append(d)
        return d

    def parse_plugin(self, plugin_path, encoding='utf-8'):
        if isinstance(plugin_path, Path):
            plugin_php_path = plugin_path / 'plugin.php'
        else:
            plugin_php_path = f"{plugin_path}/plugin.php"

        plugin_php_dict = self.parse_plugin_php(plugin_php_path, encoding)
        plugin_php_dict['remotes'] = self._git_helper.parse_git_remotes(plugin_path)
        # replace last entry in plugin.php list with our extended version
        self._current_installation['plugin.php'][-1:] = plugin_php_dict
        return plugin_php_dict

    def parse_plugin_php(self, file_path, encoding='utf-8'):
        """Returns plugin information

        :param file_path: path to plugin.php file
        :type file_path: str
        :param encoding: encoding of file
        :type encoding: str
        :return: dict with plugin version, compatible ILIAS versions and author information
        :rtype: dict
        """
        d = {"source_file": file_path}

        with open(file_path, encoding=encoding) as plugin_php:
            for i, line in enumerate(plugin_php):
                if i == 0:
                    continue
                result_php_var = re.search(r"\$(\w+)\s+?=\s+?[\"']([a-zA-Z\@\s\.]+|[0-9\.]+)[\"'];", line)
                result_define = re.search(r"define\(['\"]([a-zA-Z_]+)['\"],\s?['\"]([0-9\.]+)['\"]\);", line)
                if result_php_var:
                    d[result_php_var.groups()[0]] = result_php_var.groups()[1]
                if result_define:
                    d[result_define.groups()[0]] = result_define.groups()[1]

        self._current_installation['plugin.php'].append(d)
        return d

    def parse_version(self, file_path):
        """Returns the ILIAS version from file

        :param file_path: path to an inc.ilias_version.php file
        :return: version
        :rtype: str
        """

        version = re.search(r"\"(\d\.[\d\.?]+)\"", open(file_path).read()).groups()[0]
        self._current_installation['ilias-version']: version
        return version

    def parse_gitmodules(self, file_path):
        """Parses .gitmodules file and returns information for each submodule there

        :param file_path: path to .gitmodules file
        :type file_path: str
        :return: {'submodule_name': {'path': '/path/to/submodule', 'url': 'git_project_url', 'branch': 'branch_name'}}
        :rtype: dict
        """
        d = {}
        with open(file_path, 'r') as gitmodules:
            text = gitmodules.read()

            names = re.findall(r"\[submodule\s\"(\w+)\"]", text)
            path_groups = re.findall(r"(path)\s=\s([\w+/]+)", text)
            url_groups = re.findall(r"(url)\s=\s([./]+[\w/.]+)", text)
            branch_groups = re.findall(r"(branch)\s=\s([\w /.]+)", text)

            for i in range(len(names)):
                d[names[i]] = {
                    path_groups[i][0]: path_groups[i][1],
                    url_groups[i][0]: url_groups[i][1],
                    branch_groups[i][0]: branch_groups[i][1]
                }

        self._current_installation['submodules'] = d
        return d


class IliasPathFinder:

    def __init__(self, excluded_folders=None):
        """
        :param excluded_folders: list of folders to skip
        :type excluded_folders: list
        """
        self._ilias_paths = {}
        self._excluded = excluded_folders or ['_Examples']

    __slots__ = ('_ilias_paths', '_excluded')

    def __iter__(self):
        return self

    def __next__(self):
        while self._ilias_paths:
            for path, d in self._ilias_paths.items():
                del self._ilias_paths[path]
                return path, d
        else:
            raise StopIteration

    @property
    def ilias_paths(self):
        return deepcopy(self._ilias_paths)

    def find_installations(self, start_path, excluded_folders=None):
        """Recursively searches a path for all ILIAS installations

        Any path containing a value that is in self.exclude_dirs, is skipped. This happens to account for backups,
        Skip irrelevant paths to speed up execution and enable us to customize which installations should be skipped

        :param start_path: path to start searching from. In most cases "/" is the best option
        :type start_path: str
        :param excluded_folders: list of folders to skip while searching
        :type excluded_folders: list
        :return: yields full path to each found ILIAS installation
        :rtype: str
        """

        # TODO could add behaviour to only find active installations based on the presence of ilias.ini.php
        excluded_dirs = self._extend_excluded_folders(excluded_folders)
        excluded_dirs.append('Customizing/global')
        ilias_paths = []

        for file in find_files_recursive(str(start_path), 'ilias.php', excluded_dirs):
            ilias_path = osp.dirname(file)
            if ilias_path not in self._ilias_paths:
                self._ilias_paths[ilias_path] = {'plugins': {}, 'files': self._find_analyzable_files(ilias_path)}
            ilias_paths.append(ilias_path)
        return ilias_paths

    def find_plugins(self, start_path, excluded_folders=None):
        """Recursively searches a path for all ILIAS plugins

        :param start_path: path to start searching from. In most cases "/" is the best option
        :type start_path: str
        :param excluded_folders: list of folders to skip while searching
        :type excluded_folders: list
        :return: yields full path to each found ILIAS installation
        :rtype: str
        """
        excluded_dirs = self._extend_excluded_folders(excluded_folders)
        plugin_paths = []

        for file in find_files_recursive(start_path, 'plugin.php', excluded_dirs):
            plugin_path = osp.dirname(file)
            plugin_paths.append(plugin_path)
            for path, d in self._ilias_paths.items():
                if path in plugin_path:
                    d['plugins'][osp.basename(plugin_path)] = file

        return plugin_paths

    def _find_analyzable_files(self, ilias_path):
        d = {
            '.gitmodules': osp.join(ilias_path, '.gitmodules'),
            'ilias.ini.php': osp.join(ilias_path, 'ilias.ini.php'),
            'inc.ilias_version.php': osp.join(ilias_path, 'include', 'inc.ilias.version.php'),
            'client.ini.php': []
        }

        for client_ini in find_files_recursive(ilias_path, 'client.ini.php'):
            d['client.ini.php'].append(client_ini)
        return d

    def _extend_excluded_folders(self, excluded_folders):
        excluded_dirs = deepcopy(self._excluded)
        if excluded_folders and isinstance(excluded_folders, list):
            excluded_dirs.extend(excluded_folders)
        return excluded_dirs


class GitHelper:

    def __init__(self):
        self._data = {}

    __slots__ = '_data'

    @property
    def data(self):
        return deepcopy(self._data)

    def parse_git_remotes(self, repo_path):
        try:
            if "run" in dir(subprocess):
                # CalledProcessError
                cp = subprocess.run(['git', 'remote', '-v'], cwd=repo_path, stdout=subprocess.PIPE)
                return self._format_git_remote_to_dict(cp.stdout.decode('utf8'))
            else:
                cp = subprocess.check_output(['git', 'remote', '-v'], cwd=repo_path)
                return self._format_git_remote_to_dict(str(cp, 'utf-8'))
        except subprocess.CalledProcessError as err:
            print(err)
            return ""

    def _format_git_remote_to_dict(self, remote_str):
        remote_dict = {}
        lines = remote_str.splitlines()
        formatted_lines = [tuple(l.split(' ')[0].split('\t')) for l in lines]

        for line in formatted_lines:
            remote_dict.update({line[0]: line[1]})
        return remote_dict
