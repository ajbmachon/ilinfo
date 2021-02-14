# Created by Andre Machon 14/02/2021
import pytest as pt

from os import path as osp
from ilinfo import IliasFileParser, GitHelper
from tests.fixtures import ilias_ini_path, client_ini_path, plugin_php_path


class TestGitHelper:
    def setup(self):
        self.git_helper = GitHelper()

    def test_init(self):
        assert self.git_helper


class TestIliasFileParser:
    def setup(self):
        self.file_parser = IliasFileParser()

    def test_init(self):
        assert self.file_parser

    def test_parse_ilias_ini(self, ilias_ini_path):
        ini_dict = self.file_parser.parse_ilias_ini(ilias_ini_path)
        assert isinstance(ini_dict, dict)
        assert ini_dict == {
            'clients': {'datadir': '/srv/www/seminar/data', 'default': 'CLIENT_NAME', 'inifile': 'client.ini.php',
                        'path': 'data'}, 'debian': {}, 'https': {}, 'log': {}, 'redhat': {},
            'server': {'absolute_path': '/srv/www/ilias', 'http_path': 'https://ilias.website.net'}, 'setup': {},
            'source_file': ilias_ini_path, 'suse': {},
            'tools': {}}

    def test_parse_client_ini(self, client_ini_path):
        ini_dict = self.file_parser.parse_client_ini(client_ini_path)
        assert ini_dict == {'auth': {}, 'cache': {}, 'cache_activated_components': {},
                            'client': {'access': '1', 'name': 'CLIENT_NAME'},
                            'db': {'host': 'localhost', 'name': 'generic_db_name_123', 'pass': 'generic_password_123',
                                   'port': '', 'type': 'innodb', 'user': 'generic_user_123'},
                            'language': {'default': 'de'}, 'layout': {'skin': 'default', 'style': 'delos'},
                            'server': {}, 'session': {},
                            'source_file': client_ini_path,
                            'system': {}}

    def test_parse_plugin_php(self, plugin_php_path):
        plugin_info_dict = self.file_parser.parse_plugin_php(plugin_php_path)
        assert plugin_info_dict == {'source_file': plugin_php_path, 'ilias_max_version': '5.4.999',
                                    'ilias_min_version': '5.3.0', 'responsible': 'Andre Machon', 'version': '1.1.0'}
