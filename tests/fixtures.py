# Created by Andre Machon 14/02/2021
import pytest as pt
import os.path as osp

FIXTURE_FILES_DIR = osp.join(osp.dirname(osp.realpath(__file__)), 'fixture-files')

@pt.fixture
def ilias_ini_path():
    return osp.join(FIXTURE_FILES_DIR, 'ilias.ini.php')

@pt.fixture
def client_ini_path():
    return osp.join(FIXTURE_FILES_DIR, 'client.ini.php')

@pt.fixture
def plugin_php_path():
    return osp.join(FIXTURE_FILES_DIR, 'plugin.php')

@pt.fixture
def inc_ilias_version_php_path():
    return osp.join(FIXTURE_FILES_DIR, 'inc.ilias_version.php')

@pt.fixture
def gitmodules_path():
    return osp.join(FIXTURE_FILES_DIR, '.gitmodules')

