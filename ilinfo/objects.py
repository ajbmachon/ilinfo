# Created by Andre Machon 14/02/2021
import re
import subprocess
from os import path as osp
from copy import deepcopy

from ilinfo.utils import parse_ini_to_dict, find_files_recursive

__all__ = ['IliasFileParser', 'IliasPathFinder', 'GitHelper']


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

    __slots__ = '_data'

    @property
    def data(self):
        return deepcopy(self._data)

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
        self._data['ilias.ini.php'] = d
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
        self._data['client.ini.php'] = d
        return d

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

        self._data['plugin.php'] = d
        return d

    def parse_version(self, file_path):
        """Returns the ILIAS version from file

        :param file_path: path to an inc.ilias_version.php file
        :return: version
        :rtype: str
        """

        version = re.search(r"\"(\d\.[\d\.?]+)\"", open(file_path).read()).groups()[0]
        self._data['ilias-version']: version
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

        self._data['submodules'] = d
        return d


class IliasPathFinder:

    def __init__(self, excluded_folders=None):
        """
        :param excluded_folders: list of folders to skip
        :type excluded_folders: list
        """
        self._ilias_paths = {}
        self._excluded = excluded_folders or []

    __slots__ = ('_ilias_paths', '_excluded')

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

        for file in find_files_recursive(start_path, 'ilias.php', excluded_dirs):
            ilias_path = osp.dirname(file)
            if ilias_path not in self._ilias_paths:
                self._ilias_paths[ilias_path] = {'plugins': {}, 'files': self._find_analyzable_files(ilias_path)}
            yield ilias_path

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

        for file in find_files_recursive(start_path, 'plugin.php', excluded_dirs):
            plugin_path = osp.dirname(file)
            for path, d in self._ilias_paths:
                if path in plugin_path:
                    d['plugins'][osp.basename(plugin_path)] = file

            yield plugin_path

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
