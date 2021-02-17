# Created by Andre Machon 16/02/2021
from abc import ABC, abstractmethod
from copy import deepcopy
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
        self._combined_dict = {}
        super().__init__(ilias_dicts)

        package_folder = Path(__file__).parents[1]
        self._output_path = Path(output_path) if output_path else package_folder / 'ilinfo-results'

        if not self._output_path.exists():
            self._output_path.mkdir(parents=True, exist_ok=True)

    @property
    def ilias_dicts(self):
        return deepcopy(self._ilias_dicts)

    @ilias_dicts.setter
    def ilias_dicts(self, new_dict):
        self._ilias_dicts.append(new_dict)

    def combine_data(self, ilias_dicts):
        # combine ilias_info_dicts data to single dict
        pass

    def output_data(self):
        # output data to specified directory
        pass
