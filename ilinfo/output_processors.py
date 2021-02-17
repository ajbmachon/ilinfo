# Created by Andre Machon 16/02/2021
from abc import ABC, abstractmethod
from pathlib import Path

__all__ = ['OutputProcessor', 'JSONOutput']


class OutputProcessor(ABC):
    def __init__(self, ilias_dicts=None):
        self._ilias_dicts = ilias_dicts

    @abstractmethod
    def combine_data(self, ilias_dicts):
        pass

    @abstractmethod
    def output_data(self):
        pass


class JSONOutput(OutputProcessor):
    def __init__(self, ilias_dicts=None, output_path=None):
        super().__init__(ilias_dicts)
        package_folder = Path(__file__).parents[1]
        self._output_path = output_path or package_folder / 'ilinfo-results'
        if not self._output_path.exists():
            self._output_path.mkdir(parents=True, exist_ok=True)

    def combine_data(self, ilias_dicts):
        # combine ilias_info_dicts data to single dict
        pass

    def output_data(self):
        # output data to specified directory
        pass
