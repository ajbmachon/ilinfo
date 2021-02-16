# Created by Andre Machon 16/02/2021
import pytest as pt
from ilinfo.output_processors import OutputProcessor

class TestOutputProcessor:
    def test_output_processor_cannot_be_instantiated(self):
        with pt.raises(TypeError):
            OutputProcessor([])


class TestJsonOutputProcessor:
    pass
