import hashlib
import json
import os
from typing import Any


def ns_hash(name: str, length=40) -> str:
    hash: str = hashlib.sha1(name.encode("UTF-8")).hexdigest()
    return hash[:length]


class Infinity:
    _instance = None  # This will hold the singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Infinity, cls).__new__(cls)
        return cls._instance

    # Make it behave like an integer for comparisons
    def __lt__(self, other):
        return False  # Anything is less than Infinity

    def __gt__(self, other):
        return True  # Infinity is always greater than anything else

    def __eq__(self, other):
        return False  # Infinity is never equal to anything else

    def __le__(self, other):
        return False  # Infinity is never less than or equal to anything else

    def __ge__(self, other):
        return True  # Infinity is always greater than or equal to anything else

    def __repr__(self):
        return "Infinity"


# Singleton instance of Infinity
infinity = Infinity()


def get_all_package_names(max: int = 300, offset: int = 0) -> set[str]:
    names = set()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path + "/package_cache/names.json")
    min = max
    max = offset + max
    with open(file_path) as file:
        data = json.load(file)
        i: int = 0
        for package_name in data:
            i += 1
            if i < min:
                continue
            names.add(package_name)
            if i >= max:
                break
    print(
        f"created a set of all package names with {len(names)} elements."
        f"This is {i-len(names)} less than the original file"
    )
    return names


def find_duplicates(lst: list[Any]):
    seen = set()
    duplicates = set()

    for item in lst:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)

    return duplicates
