# Created by Andre Machon 16/02/2021
import json
import pytest as pt
from pathlib import Path
from ilinfo.output_processors import OutputProcessor
from ilinfo import JSONOutput, IliasFileParser, IliasPathFinder


class TestOutputProcessor:
    def test_output_processor_cannot_be_instantiated(self):
        with pt.raises(TypeError):
            OutputProcessor([])


class TestJsonOutputProcessor:
    def setup(self):
        self.out_path = '/tmp/ilinfo-results'
        self.json_out = JSONOutput([{}, {}], output_path=self.out_path)

    def test_init(self):
        assert self.json_out
        # TODO more asserts

    def test_ilias_dicts(self):
        self.json_out.ilias_dicts = {'test': 'dict'}
        assert self.json_out.ilias_dicts == [{}, {}, {'test': 'dict'}]

    def test_output_data(self, setup_fake_plugin):
        finder = IliasPathFinder()
        parser = IliasFileParser()
        plugin_path = setup_fake_plugin("FakePlugin1")
        il_path = plugin_path.parents[6]

        finder.find_installations(il_path)
        finder.find_plugins(il_path)
        results = parser.parse_from_pathfinder(finder)
        ilias_path, result = list(results.items())[0]

        success = self.json_out.output_data(file_parser=parser)
        file_path = Path(self.out_path) / 'ilinfo.json'
        assert success
        assert Path.is_file(file_path) is True
        assert json.load(open(file_path, 'r')) == {
            ilias_path: {
                'ilias_path': ilias_path,
                'client.ini.php': [
                    {
                        'source_file': result.get('client.ini.php', {})[0].get('source_file'),
                        'server': {}, 'client': {'name': 'CLIENT_NAME', 'access': '1'},
                        'db': {'type': 'innodb', 'host': 'localhost', 'user': 'generic_user_123',
                               'pass': 'generic_password_123', 'name': 'generic_db_name_123', 'port': ''}, 'auth': {},
                        'language': {'default': 'de'}, 'layout': {'skin': 'default', 'style': 'delos'}, 'session': {},
                        'system': {}, 'cache': {}, 'cache_activated_components': {}
                    }
                ],
                'plugin.php': [
                    'source_file', 'version', 'ilias_min_version', 'ilias_max_version', 'responsible', 'remotes'
                ],
                'ilias.ini.php': {
                    'source_file': result.get('ilias.ini.php', {}).get('source_file'),
                    'server': {'http_path': 'https://ilias.website.net', 'absolute_path': '/srv/www/ilias'},
                    'clients': {'path': 'data', 'inifile': 'client.ini.php', 'datadir': '/srv/www/seminar/data',
                                'default': 'CLIENT_NAME'}, 'setup': {}, 'tools': {}, 'log': {}, 'debian': {},
                    'redhat': {}, 'suse': {}, 'https': {}}, 'submodules': {
                    'DBASManager': {
                        'path': 'Customizing/global/plugins/Services/UIComponent/UserInterfaceHook/DBASManager',
                        'url': '../../../iliasaddons/DBASManager.git', 'branch': 'Release_7.0'
                    },
                    'LearnerGuidance': {
                        'path': 'Customizing/global/plugins/Services/UIComponent/UserInterfaceHook/LearnerGuidance',
                        'url': '../../../iliasaddons/LearnerGuidance.git', 'branch': 'Release_7.0'
                    },
                    'CountryLicenseTypes': {
                        'path': 'Customizing/global/plugins/Services/Cron/CronHook/CountryLicenseTypes',
                        'url': '../plugins/CountryLicenseTypes.git',
                        'branch': 'r6'
                    },
                    'LPOverview': {
                        'path': 'Customizing/global/plugins/Services/COPage/PageComponent/LPOverview',
                        'url': '../../../iliasplugins/LPOverview.git', 'branch': 'r6'}
                }
            }
        }
