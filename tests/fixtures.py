# Created by Andre Machon 14/02/2021
import shutil
import subprocess

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

@pt.fixture
def set_up_git_plugin_repo(tmp_path):
    repo_path = tmp_path / "plugin_repo"
    repo_path.mkdir()
    f = repo_path / "temp.txt"
    f.write_text("TEST")
    shutil.copy(osp.join(osp.dirname(__file__), 'fixture-files', 'plugin.php'), repo_path)
    _create_git_repo(repo_path)
    return repo_path

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
