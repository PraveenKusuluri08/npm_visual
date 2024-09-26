import os
from pathlib import Path
from typing import Any, Dict

from flask import json


def exists(package_name: str) -> bool:
    path_to_file: str = _get_path(package_name)
    my_file = Path(path_to_file)
    return my_file.is_file()


def save(package_name: str, data):
    path_to_file: str = _get_path(package_name)
    json_object = json.dumps(data, indent=4)
    try:
        with open(path_to_file, "w+") as outfile:
            outfile.write(json_object)
    except Exception as e:
        raise e


def load(package_name: str) -> Dict[str, Any]:
    path_to_file: str = _get_path(package_name)
    # Use a try catch because file may be accessed between time we search for file and
    # the time we try to read the file
    try:
        with open(path_to_file) as open_file:
            json_object = json.load(open_file)
            return json_object
    except Exception as e:
        # file is inaccesable or does not exist
        # call scraper and wait until file is saved.
        raise e


def _get_path(package_name: str) -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    relative_path = "package_cache/" + package_name + ".json"
    return os.path.join(dir_path, relative_path)
