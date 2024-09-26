import os
import shutil
import hashlib
import string
from pathlib import Path
from typing import Any, Dict

from flask import current_app as app
from flask import json
import numpy

whitelist = set(string.ascii_letters + string.digits)
_HASH_LENGTH = 40


def _get_cache_path() -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path + "/package_cache")


cache_path = _get_cache_path()
if not os.path.exists(cache_path):
    os.mkdir(cache_path)


def exists(package_name: str) -> bool:
    path_to_file: str = _get_package_path(package_name)
    my_file = Path(path_to_file)
    return my_file.is_file()


def save(package_name: str, data):
    path_to_file: str = _get_package_path(package_name)
    json_object = json.dumps(data, indent=4)
    try:
        with open(path_to_file, "w+") as outfile:
            outfile.write(json_object)
    except Exception as e:
        raise e


def load(package_name: str) -> Dict[str, Any]:
    path_to_file: str = _get_package_path(package_name)
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


def clear_cache():
    for filename in os.listdir(cache_path):
        file_path = os.path.join(cache_path, filename)
        clean_package_cache(file_path)


def clean_package_cache(file_path):
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        app.logger.error(f"Failed to delete {file_path}. Reason: {e}")


def _get_package_path(package_name: str) -> str:
    filename = _convert_to_filename(package_name)
    return os.path.join(cache_path, filename + ".json")


def _hash_package(package_name: str) -> str:
    hash: str = hashlib.sha1(package_name.encode("UTF-8")).hexdigest()
    return hash[:_HASH_LENGTH]


def _convert_to_filename(package_name: str) -> str:
    # for readability, keep some of the filename
    filename = _whitelist(package_name)
    file_hash = str(_hash_package(package_name))
    # Most OS have maximum file lengths. make sure it is under 255
    if len(filename) + _HASH_LENGTH > 254:
        filename_new_len = 254 - _HASH_LENGTH
        filename = filename[:filename_new_len]

    return filename + "_" + file_hash


def _whitelist(package_name: str) -> str:
    return "".join(c for c in package_name if c in whitelist)
