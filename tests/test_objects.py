# Created by Andre Machon 14/02/2021
import subprocess

import pytest as pt

from os import path as osp
from ilinfo import IliasFileParser, IliasPathFinder, GitHelper
from tests.fixtures import \
    ilias_ini_path, \
    client_ini_path, \
    plugin_php_path, \
    inc_ilias_version_php_path, \
    gitmodules_path


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

    def test_find_installations(self, tmp_path):
        ilias_path_1 = self._create_fake_ilias_in_filesystem(tmp_path / 'ILIAS_1')
        ilias_path_2 = self._create_fake_ilias_in_filesystem(tmp_path / 'ILIAS_2')

        ilias_paths_itr = self.pathfinder.find_installations(tmp_path)
        assert next(ilias_paths_itr) == str(ilias_path_1)
        assert next(ilias_paths_itr) == str(ilias_path_2)

        files = self.pathfinder.ilias_paths[str(ilias_path_1)]['files']
        assert '.gitmodules' in files
        assert 'ilias.ini.php' in files
        assert 'inc.ilias_version.php' in files
        assert 'client.ini.php' in files

    def test_find_plugins(self, tmp_path):
        plugin_path_1 = self._create_fake_plugin_in_filesystem(tmp_path / 'ILIAS_1')
        plugin_path_2 = self._create_fake_plugin_in_filesystem(tmp_path / 'ILIAS_2')

        plugin_path_itr = self.pathfinder.find_plugins(tmp_path)
        assert next(plugin_path_itr) == str(plugin_path_1)
        assert next(plugin_path_itr) == str(plugin_path_2)


    def _create_fake_ilias_in_filesystem(self, path):
        path.mkdir(parents=True)
        p2 = path / 'include'
        p2.mkdir(parents=True)
        p3 = path / 'data/example_client'
        p3.mkdir(parents=True)

        f = path / "ilias.php"
        f.touch()

        f = path / ".gitmodules"
        f.touch()

        f = p2 / "inc.ilias_version.php"
        f.touch()

        f = p3 / "client.ini.php"
        f.touch()

        return path

    def _create_fake_plugin_in_filesystem(self, path):
        ilias_path = self._create_fake_ilias_in_filesystem(path)
        plugin_path = ilias_path / 'Customizing/global/plugins/Services/UIComponent/UserInterfaceHook/UserTakeOver'
        plugin_path.mkdir(exist_ok=True, parents=True)
        f = plugin_path / "plugin.php"
        f.touch()
        return plugin_path


class TestGitHelper:
    def setup(self):
        self.git_helper = GitHelper()

    def test_init(self):
        assert self.git_helper

    def test_parse_git_remotes(self, tmp_path):
        repo_path = self._set_up_git_plugin_repo(tmp_path)
        remotes = self.git_helper.parse_git_remotes(repo_path)
        assert remotes == {'alternate': 'https://github.com/Amstutz/ILIAS.git/ILIAS-eLearning/ILIAS.git', 'origin': 'https://github.com/ILIAS-eLearning/ILIAS.git'}

    def _set_up_git_plugin_repo(self, path):
        repo_path = path / "plugin_repo"
        repo_path.mkdir()
        f = repo_path / "temp.txt"
        f.write_text("TEST")
        self._create_git_repo(repo_path)
        return repo_path

    def _create_git_repo(self, path):
        if "run" in dir(subprocess):
            subprocess.run(['git', 'init'], cwd=path, stdout=subprocess.PIPE)
            subprocess.run(['git', 'add', '.'], cwd=path, stdout=subprocess.PIPE)
            cp = subprocess.run(['git', 'commit', '-m', 'Initial Commit'], cwd=path, stdout=subprocess.PIPE)
            subprocess.run(['git', 'remote', 'add', 'origin', 'https://github.com/ILIAS-eLearning/ILIAS.git'], cwd=path,
                           stdout=subprocess.PIPE)
            subprocess.run(
                ['git', 'remote', 'add', 'alternate', 'https://github.com/Amstutz/ILIAS.git/ILIAS-eLearning/ILIAS.git'],
                cwd=path,
                stdout=subprocess.PIPE
            )
            return cp.stdout.decode('utf8')
        else:
            subprocess.check_output(['git', 'remote', '-v'], cwd=path)
            subprocess.check_output(['git', 'add', '.'], cwd=path)
            cp = subprocess.check_output(['git', 'commit', '-m', 'Initial Commit'], cwd=path)
            subprocess.check_output(['git', 'remote', 'add', 'origin', 'https://github.com/ILIAS-eLearning/ILIAS.git'],
                                    cwd=path)
            subprocess.check_output(
                ['git', 'remote', 'add', 'alternate', 'https://github.com/Amstutz/ILIAS.git/ILIAS-eLearning/ILIAS.git'],
                cwd=path
            )
            return str(cp, 'utf-8')
