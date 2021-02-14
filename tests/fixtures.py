# Created by Andre Machon 14/02/2021
import pytest as pt
import os.path as osp


@pt.fixture
def ilias_ini_path():
    return osp.join(osp.dirname(osp.realpath(__file__)), 'fixture-files', 'ilias.ini.php')
