# Created by Andre Machon 14/02/2021
import configparser
import re

from ilinfo.utils import parse_ini_to_dict

__all__ = ['IliasFileParser', 'GitHelper']


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


class GitHelper:
    pass
