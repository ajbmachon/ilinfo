# Created by Andre Machon 16/02/2021
import pytest as pt
from ilinfo.output_processors import OutputProcessor
from ilinfo import JSONOutput, IliasFileParser


class TestOutputProcessor:
    def test_output_processor_cannot_be_instantiated(self):
        with pt.raises(TypeError):
            OutputProcessor([])


class TestJsonOutputProcessor:
    def setup(self):
        out_path = '/tmp/pytest-of-amachon/ilinfo-results'
        self.json_out = JSONOutput([{}, {}], output_path=out_path)

    def test_init(self):
        assert self.json_out
        # TODO more asserts

    def test_ilias_dicts(self):
        self.json_out.ilias_dicts = {'test': 'dict'}
        assert self.json_out.ilias_dicts == [{}, {}, {'test': 'dict'}]
