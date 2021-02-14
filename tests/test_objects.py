# Created by Andre Machon 14/02/2021
import pytest as pt

from os import path as osp
from ilinfo import IliasFileParser, GitHelper
from tests.fixtures import ilias_ini_path

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
