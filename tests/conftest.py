# Created by Andre Machon 14/02/2021
import shutil
import subprocess

import pytest as pt
import os.path as osp
from pathlib import Path

# FIXTURE_FILES_DIR = osp.join(osp.dirname(osp.realpath(__file__)), 'fixtures')
FIXTURE_FILES_DIR = Path(osp.dirname(osp.realpath(__file__))) / 'fixtures'


def _copy(self, target):
    import shutil
    assert self.is_file()
    shutil.copy(str(self), str(target))  # str() only there for Python < (3, 6)


Path.copy = _copy


@pt.fixture
def ilias_ini_path():
    return FIXTURE_FILES_DIR / 'ilias.ini.php'


@pt.fixture
def inc_ilias_version_php_path():
    return FIXTURE_FILES_DIR / 'inc.ilias_version.php'


@pt.fixture
def client_ini_path():
    return FIXTURE_FILES_DIR / 'client.ini.php'


@pt.fixture
def plugin_php_path():
    return FIXTURE_FILES_DIR / 'plugin.php'


@pt.fixture
def gitmodules_path():
    return FIXTURE_FILES_DIR / '.gitmodules'


@pt.fixture
def setup_fake_ilias(tmp_path, ilias_ini_path, inc_ilias_version_php_path, client_ini_path, gitmodules_path):
    def _fake_ilias(path=""):
        ilias_path, include_path, client_data_path = _create_ilias_dirs(tmp_path / path)
        ilias_ini_path.copy(ilias_path / 'ilias.ini.php')
        gitmodules_path.copy(ilias_path / '.gitmodules')
        inc_ilias_version_php_path.copy(include_path / 'inc.ilias_version.php')
        client_ini_path.copy(client_data_path / 'client.ini.php')
        f = ilias_path / 'ilias.php'
        f.touch()

        return ilias_path

    return _fake_ilias


@pt.fixture
def setup_fake_plugin(setup_fake_ilias, plugin_php_path):
    def _fake_plugin(name="TestPlugin"):
        ilias_path = setup_fake_ilias()
        plugin_path = ilias_path / f'Customizing/global/plugins/Services/UIComponent/UserInterfaceHook/{name}'
        plugin_path.mkdir(exist_ok=True, parents=True)
        plugin_php_path.copy(plugin_path / "plugin.php")
        return plugin_path

    return _fake_plugin


@pt.fixture
def setup_git_plugin_repo(setup_fake_plugin):
    plugin_path = setup_fake_plugin("UserTakeOver")
    _create_git_repo(plugin_path)
    return plugin_path


def _create_ilias_dirs(path):
    path = path / 'ILIAS'
    path.mkdir(parents=True, exist_ok=True)
    p2 = path / 'include'
    p2.mkdir(parents=True, exist_ok=True)
    p3 = path / 'data/example_client'
    p3.mkdir(parents=True, exist_ok=True)
    return path, p2, p3


def _create_git_repo(path):
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
