# Created by Andre Machon 14/02/2021
import pytest as pt
from os import path as osp
from pathlib import Path
from ilinfo import IliasFileParser, IliasPathFinder, GitHelper, IliasAnalyzer


class TestIliasAnalyzer:
    def setup(self):
        self.analyzer = IliasAnalyzer()

    def test_init(self):
        assert self.analyzer

        with pt.raises(TypeError):
            IliasAnalyzer(IliasFileParser(), "", "", "", "")
            IliasAnalyzer(1, "", GitHelper(), "")


class TestIliasFileParser:
    def setup(self):
        self.file_parser = IliasFileParser()

    def test_init(self):
        assert self.file_parser

    def test_parse_from_pathfinder(self, setup_fake_ilias):
        ilias_path = setup_fake_ilias("Customer_1")
        pathfinder = IliasPathFinder()
        pathfinder.find_installations(ilias_path)
        pathfinder.find_plugins(ilias_path)
        results = self.file_parser.parse_from_pathfinder(pathfinder)

        assert results == {'client.ini.php': [{'auth': {}, 'cache': {}, 'cache_activated_components': {},
                                               'client': {'access': '1', 'name': 'CLIENT_NAME'},
                                               'db': {'host': 'localhost', 'name': 'generic_db_name_123',
                                                      'pass': 'generic_password_123', 'port': '', 'type': 'innodb',
                                                      'user': 'generic_user_123'}, 'language': {'default': 'de'},
                                               'layout': {'skin': 'default', 'style': 'delos'}, 'server': {},
                                               'session': {},
                                               'source_file': results.get('client.ini.php', {})[0].get('source_file'),
                                               'system': {}}], 'ilias.ini.php': {
            'clients': {'datadir': '/srv/www/seminar/data', 'default': 'CLIENT_NAME', 'inifile': 'client.ini.php',
                        'path': 'data'}, 'debian': {}, 'https': {}, 'log': {}, 'redhat': {},
            'server': {'absolute_path': '/srv/www/ilias', 'http_path': 'https://ilias.website.net'}, 'setup': {},
            'source_file': results.get('ilias.ini.php', {}).get('source_file'),
            'suse': {}, 'tools': {}},
                           'plugin.php': [],
                           'submodules': {
                               'CountryLicenseTypes': {
                                   'branch': 'r6',
                                   'path': 'Customizing/global/plugins/Services/Cron/CronHook/CountryLicenseTypes',
                                   'url': '../plugins/CountryLicenseTypes.git'},
                               'DBASManager': {
                                   'branch': 'Release_7.0',
                                   'path': 'Customizing/global/plugins/Services/UIComponent/UserInterfaceHook/DBASManager',
                                   'url': '../../../iliasaddons/DBASManager.git'},
                               'LPOverview': {
                                   'branch': 'r6',
                                   'path': 'Customizing/global/plugins/Services/COPage/PageComponent/LPOverview',
                                   'url': '../../../iliasplugins/LPOverview.git'},
                               'LearnerGuidance': {
                                   'branch': 'Release_7.0',
                                   'path': 'Customizing/global/plugins/Services/UIComponent/UserInterfaceHook/LearnerGuidance',
                                   'url': '../../../iliasaddons/LearnerGuidance.git'}
                           }}

        with pt.raises(TypeError):
            self.file_parser.parse_from_pathfinder("/tmp/exmaple/path")

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

    def test_parse_plugin(self, setup_git_plugin_repo):
        plugin_info_dict = self.file_parser.parse_plugin(setup_git_plugin_repo)
        assert plugin_info_dict == {'source_file': setup_git_plugin_repo / 'plugin.php', 'ilias_max_version': '5.4.999',
                                    'ilias_min_version': '5.3.0', 'responsible': 'Andre Machon', 'version': '1.1.0',
                                    'remotes': {
                                        'alternate': 'https://github.com/Amstutz/ILIAS.git/ILIAS-eLearning/ILIAS.git',
                                        'origin': 'https://github.com/ILIAS-eLearning/ILIAS.git'
                                    }}

    def test_parse_plugin_php(self, plugin_php_path):
        plugin_info_dict = self.file_parser.parse_plugin_php(plugin_php_path)
        assert plugin_info_dict == {'source_file': plugin_php_path, 'ilias_max_version': '5.4.999',
                                    'ilias_min_version': '5.3.0', 'responsible': 'Andre Machon', 'version': '1.1.0'}

    def test_parse_ilias_version(self, inc_ilias_version_php_path):
        version = self.file_parser.parse_version(inc_ilias_version_php_path)
        assert version == '6.6'

    def test_parse_gitmodules(self, gitmodules_path):
        submodule_dict = self.file_parser.parse_gitmodules(gitmodules_path)
        assert submodule_dict == {
            'DBASManager': {
                'path': 'Customizing/global/plugins/Services/UIComponent/UserInterfaceHook/DBASManager',
                'url': '../../../iliasaddons/DBASManager.git', 'branch': 'Release_7.0'},
            'LearnerGuidance': {
                'path': 'Customizing/global/plugins/Services/UIComponent/UserInterfaceHook/LearnerGuidance',
                'url': '../../../iliasaddons/LearnerGuidance.git', 'branch': 'Release_7.0'},
            'CountryLicenseTypes': {
                'path': 'Customizing/global/plugins/Services/Cron/CronHook/CountryLicenseTypes',
                'url': '../plugins/CountryLicenseTypes.git', 'branch': 'r6'},
            'LPOverview': {
                'path': 'Customizing/global/plugins/Services/COPage/PageComponent/LPOverview',
                'url': '../../../iliasplugins/LPOverview.git', 'branch': 'r6'}
        }


class TestIliasPathFinder:
    # TODO expand tests to verify skipping of excluded folders!
    def setup(self):
        self.pathfinder = IliasPathFinder()

    def test_init(self):
        assert self.pathfinder

    def test_iteration(self, setup_fake_ilias):
        ilias_path_1 = setup_fake_ilias('Customer_1')
        ilias_path_2 = setup_fake_ilias('Customer_2')
        ilias_paths = self.pathfinder.find_installations(osp.dirname(osp.dirname(ilias_path_1)))

        il_path, il_dict = next(self.pathfinder)
        assert il_path == str(ilias_path_1)
        assert isinstance(il_dict, dict)
        il_path, il_dict = next(self.pathfinder)
        assert il_path == str(ilias_path_2)

    def test_find_installations(self, setup_fake_ilias):
        ilias_path_1 = setup_fake_ilias('Customer_1')
        ilias_path_2 = setup_fake_ilias('Customer_2')
        ilias_paths = self.pathfinder.find_installations(osp.dirname(osp.dirname(ilias_path_1)))

        assert ilias_paths[0] == str(ilias_path_1)
        assert ilias_paths[1] == str(ilias_path_2)

        files = self.pathfinder.ilias_paths[str(ilias_path_1)]['files']
        assert '.gitmodules' in files
        assert 'ilias.ini.php' in files
        assert 'inc.ilias_version.php' in files
        assert 'client.ini.php' in files

    def test_find_plugins(self, tmp_path, setup_fake_plugin):
        plugin_path_1 = setup_fake_plugin("FakePlugin1")
        plugin_path_2 = setup_fake_plugin("FakePlugin2")
        print(plugin_path_1, plugin_path_2, sep="")

        plugin_paths = self.pathfinder.find_plugins(tmp_path)
        print(plugin_paths)
        assert plugin_paths[0] == str(plugin_path_1)
        assert plugin_paths[1] == str(plugin_path_2)


class TestGitHelper:
    def setup(self):
        self.git_helper = GitHelper()

    def test_init(self):
        assert self.git_helper

    def test_parse_git_remotes(self, setup_git_plugin_repo):
        remotes = self.git_helper.parse_git_remotes(setup_git_plugin_repo)
        assert remotes == {'alternate': 'https://github.com/Amstutz/ILIAS.git/ILIAS-eLearning/ILIAS.git',
                           'origin': 'https://github.com/ILIAS-eLearning/ILIAS.git'}
