# Created by Andre Machon 14/02/2021
import configparser
from ilinfo.utils import parse_ini_to_dict

__all__ = ['IliasFileParser', 'GitHelper']


class IliasFileParser:
    """Parses ILIAS files into dictionaries

    PARSED FILES:
        ilias.ini.php
        client.ini.php
        inc.ilias_version.php
        plugin.php

    """

    def __init__(self):
        self._data = {}

    def parse_ilias_ini(self, file_path):
        d = parse_ini_to_dict(file_path, {
        "server": ['http_path', 'absolute_path'],
        "clients": ['path', 'inifile', 'datadir', 'default']
    })
        self._data['ilias.ini.php'] = d
        return d



class GitHelper:
    pass
