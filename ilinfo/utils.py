# Created by Andre Machon 07/02/2021
import mysql.connector as db_con
import configparser
from mysql.connector import errorcode
from os import path as osp
try:
    from os import scandir, walk
except ImportError:
    from scandir import scandir, walk


def mysql_safe_connect(con_dict):
    try:
        con = db_con.connect(**con_dict)
        return con
    except db_con.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password", err)
            # print("Connection Dict", con_dict)
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)


def read_client_db_login(file_name):
    """Reads the login credentials for ILIAS installation db, from client.ini file and returns a connection dict

    :param file_name: Full path to client.ini file
    :type file_name: str
    :return: connection dict
    """
    result = parse_ini_to_dict(file_name, parse_config={"db": ["user", "pass", "host", "name", "port"]})
    con_dict = result.get('db', {'user': '', 'pass': '', 'host': '', 'name': '', "port": ''})
    con_dict['password'] = con_dict.pop('pass')
    con_dict['database'] = con_dict.pop('name')
    # in case port is emtpy we don't want errors in the function using this dict for establishing db connection
    if con_dict['port'] == '':
        con_dict.pop('port')
    return con_dict


def connect_with_client_ini(ini_file):
    return mysql_safe_connect(read_client_db_login(ini_file))


def find_files_recursive(startpath, filename, excluded_dirs=None):
    """Recursively finds all files that match the given filename and yields the full path

    :param startpath: Path to start recursive search from
    :type startpath: str
    :param filename: Filename to search for
    :type filename: str
    :param excluded_dirs: strings that will lead to path being ignored, if path contains one of them
    :type excluded_dirs: list
    :rtype: object: generator, that iterates over found file paths (str)
    """
    if excluded_dirs is None:
        excluded_dirs = []
    for current_path, dirnames, filenames in walk(startpath):
        # skip processing files in dirs, that have exclude_dir values in their path
        if True in map(lambda excluded: excluded in current_path, excluded_dirs):
            continue
        if filename in filenames:
            yield osp.join(current_path, filename)


def parse_ini_to_dict(file_path, parse_config=None):
    """Parse ini file to dictionary

    :param file_path: path to ini file
    :type file_path: str
    :param parse_config: sections and options to include in result dict
    :type parse_config: dict
    :return: dict
    :rtype: dict
    """

    if not file_path:
        return
    if parse_config is not None:
        if not isinstance(parse_config, dict):
            raise TypeError("parse_config needs to be a dictionary")

    parser = configparser.ConfigParser()
    parser.read(file_path)
    data = {"source_file": file_path}

    for section in parser.sections():
        new_section = {}

        for option in parser.options(section):
            if parse_config:
                if section in parse_config and option in parse_config.get(section):
                    new_section[option] = parser.get(section, option).strip('"')
            else:
                new_section[option] = parser.get(section, option).strip('"')

        data[section] = new_section

    return data

