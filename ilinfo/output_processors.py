# Created by Andre Machon 16/02/2021
import json
from abc import ABC, abstractmethod
from copy import deepcopy
from pathlib import Path
from ilinfo import analyzers

__all__ = ['OutputProcessor', 'JSONOutput']


class OutputProcessor(ABC):
    def __init__(self, ilias_dicts=None):
        self._ilias_dicts = ilias_dicts

    @abstractmethod
    def combine_data(self, ilias_dicts):
        pass

    @abstractmethod
    def output_data(self, file_parser):
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

    def output_data(self, file_parser):
        """Outputs data analyzed by IliasFileParser instance to JSON file

        :param file_parser: IliasFileParser Instance filled with data
        :type file_parser: IliasFileParser
        :return:
        """
        if not isinstance(file_parser, analyzers.IliasFileParser):
            raise TypeError("Param file_parser needs to be of type IliasFileParser")
        if not file_parser.data:
            raise ValueError("IliasFileParser has no data, did you analyze an Installation with it?")

        with open(Path(self._output_path) / 'ilinfo.json', 'w') as jsonfile:
            json.dump(file_parser.data, jsonfile)
        return True
