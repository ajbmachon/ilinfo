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
def setup_fake_ilias(request, tmp_path):
    marker = request.node.get_closest_marker("sub_dir")
    if marker is None:
        path = tmp_path
    else:
        path = tmp_path / marker.args[0]

    ilias_path, include_path, client_data_path = _create_ilias_dirs(path)
    _copy_analyzable_ilias_files(ilias_path, include_path, client_data_path)
    return ilias_path


@pt.fixture
def setup_fake_plugin(setup_fake_ilias):
    ilias_path = setup_fake_ilias
    plugin_path = ilias_path / 'Customizing/global/plugins/Services/UIComponent/UserInterfaceHook/UserTakeOver'
    plugin_path.mkdir(exist_ok=True, parents=True)
    plugin_php_path().copy(plugin_path / "plugin.php")
    return plugin_path


@pt.fixture
def setup_git_plugin_repo(tmp_path, plugin_php_path):
    repo_path = tmp_path / "plugin_repo"
    repo_path.mkdir()
    f = repo_path / "temp.txt"
    f.write_text("TEST")
    plugin_php_path.copy(repo_path / 'plugin.php')
    _create_git_repo(repo_path)
    return repo_path



def _copy_analyzable_ilias_files(ilias_path, includes_path, client_data_path):
    """Copies ILIAS files to temp test directories

    :type ilias_path: Path
    :type includes_path: Path
    :type client_data_path: Path
    """
    ilias_ini_path().copy(ilias_path / 'ilias.ini.php')
    inc_ilias_version_php_path().copy(includes_path / 'inc.ilias_version.php')
    client_ini_path().copy(client_data_path / 'client.ini.php')


def _create_ilias_dirs(path):
    path = path / 'ILIAS'
    path.mkdir(parents=True)
    p2 = path / 'include'
    p2.mkdir(parents=True)
    p3 = path / 'data/example_client'
    p3.mkdir(parents=True)
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
