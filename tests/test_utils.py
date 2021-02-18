# Created by Andre Machon 14/02/2021
import pytest as pt

from ilinfo.utils import parse_ini_to_dict
from tests.conftest import ilias_ini_path


def test_ini_parsing(ilias_ini_path):
    d = parse_ini_to_dict(file_path=ilias_ini_path)
    d2 = parse_ini_to_dict(ilias_ini_path, {
        'server': ['http_path', 'timezone'],
        'clients': ['path', 'inifile']
    })

    assert d == {'source_file': ilias_ini_path,
                 'server': {'http_path': 'https://ilias.website.net', 'absolute_path': '/srv/www/ilias',
                            'presetting': '', 'timezone': 'Europe/Berlin'},
                 'clients': {'path': 'data', 'inifile': 'client.ini.php', 'datadir': '/srv/www/seminar/data',
                             'default': 'CLIENT_NAME', 'list': '0'},
                 'setup': {'pass': 'generic_setup_password_hash_123'},
                 'tools': {'convert': '/usr/bin/convert', 'zip': '/usr/bin/zip', 'unzip': '/usr/bin/unzip',
                           'java': '', 'htmldoc': '/usr/bin/htmldoc', 'ffmpeg': '/usr/bin/ffmpeg',
                           'ghostscript': '/usr/bin/gs', 'latex': '', 'vscantype': 'none', 'scancommand': '',
                           'cleancommand': 'root', 'fop': '', 'lessc': '/usr/bin/lessc',
                           'enable_system_styles_management': '1', 'phantomjs': '/usr/bin/phantomjs'},
                 'log': {'path': '/srv/www/admin/CLIENT_NAME', 'file': 'ilias.log', 'enabled': '1',
                         'level': 'WARNING', 'error_path': '/srv/www/admin/logfiles/CLIENT_NAME'},
                 'debian': {'data_dir': '/var/opt/ilias', 'log': '/var/log/ilias/ilias.log',
                            'convert': '/usr/bin/convert', 'zip': '/usr/bin/zip', 'unzip': '/usr/bin/unzip',
                            'java': '', 'htmldoc': '/usr/bin/htmldoc', 'ffmpeg': '/usr/bin/ffmpeg'},
                 'redhat': {'data_dir': '', 'log': '', 'convert': '', 'zip': '', 'unzip': '', 'java': '',
                            'htmldoc': ''},
                 'suse': {'data_dir': '', 'log': '', 'convert': '', 'zip': '', 'unzip': '', 'java': '',
                          'htmldoc': ''},
                 'https': {'auto_https_detect_enabled': '0', 'auto_https_detect_header_name': 'X-SSL',
                           'auto_https_detect_header_value': 'On'}}
    assert d2 == {'source_file': ilias_ini_path,
                  'server': {'http_path': 'https://ilias.website.net', 'timezone': 'Europe/Berlin'},
                  'clients': {'path': 'data', 'inifile': 'client.ini.php'}, 'setup': {}, 'tools': {}, 'log': {},
                  'debian': {}, 'redhat': {}, 'suse': {}, 'https': {}}

    with pt.raises(TypeError, match=r"parse_config needs to be a dictionary"):
        parse_ini_to_dict(file_path=ilias_ini_path, parse_config='invalid_argument_type')
