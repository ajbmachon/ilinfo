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
    result = parse_ini_file(file_name, parse_config={"db": ["user", "pass", "host", "name", "port"]})
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


def parse_ini_file(file_name, parse_config={}, **kwargs):
    """Parse given ini file to dictionary

    :param file_name: Full path to file
    :type file_name: str
    :param parse_config: configuration specifying which fields to read from which section
    :type parse_config: dict

    :return: Entries from given .ini file
    :rtype: dict

    Example parse_config: {"db": ["user", "pass", "host", "port"], "Log": True}
    Here we can specify a list of options to return from the section, or true to return all options.
    If no mapping is passed or dict is empty, all values will be returned
    """

    config = configparser.ConfigParser()
    config.read(file_name)
    file_data = {"source_file": file_name}
    get_option_dict = lambda s, f: (s, {f: config.get(s, f, fallback='').strip('"')})
    if not parse_config:
        # get all options for each section and loop over them
        for section, d in [get_option_dict(section, option) for section in config.sections()
                           for option in config.options(section)]:
            if file_data.get(section, False):
                file_data[section].update(d)
            else:
                file_data[section] = d
    else:
        for section_key, fields in parse_config.items():
            # if True was passed for a section, we get all the options
            if type(fields) is bool and fields is True:
                for option in config.options(section_key):
                    section_key, d = get_option_dict(section_key, option)
                    if file_data.get(section_key, False):
                        file_data[section_key].update(d)
                    else:
                        file_data[section_key] = d
            # otherwise, we just get the options specified for each section
            for field in fields:
                section, d = (get_option_dict(section_key, field))
                if file_data.get(section, False):
                    file_data[section].update(d)
                else:
                    file_data[section] = d
    return file_data



