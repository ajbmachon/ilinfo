# Created by Andre Machon 16/02/2021
from abc import ABC, abstractmethod

__all__ = ['OutputProcessor']


class OutputProcessor(ABC):
    def __init__(self, file_parsers):
        self._file_parsers = file_parsers

    @abstractmethod
    def combine_data(self):
        pass

    @abstractmethod
    def output_data(self):
        pass
