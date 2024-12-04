import hashlib
import json
import os
import shutil
from typing import Any


def nsprint(text: str, num_tabs: int = 0, tab: str = "    "):
    terminal_width = shutil.get_terminal_size().columns
    indent = tab * num_tabs
    max_line_length = terminal_width - len(indent)
    # Split the input text into separate lines based on existing newlines
    lines = text.splitlines()

    # For each line in the split lines, we will process it and wrap as necessary
    result_lines = []
    first_line = True
    for line in lines:
        while len(line) > max_line_length:
            # Find the last space within the max length to break the line without cutting words
            break_point = line.rfind(" ", 0, max_line_length)
            if break_point == -1:  # No spaces found, just break at the max length
                break_point = max_line_length

            # Add the line with the appropriate indentation
            result_lines.append(indent + line[:break_point])

            # Remove the portion of the text we've already printed
            line = line[break_point:].lstrip()
            if first_line:
                indent += tab
                max_line_length = terminal_width - len(indent)
                first_line = False

        # Add the last line (if any remaining text)
        if line:
            result_lines.append(indent + line)

    for line in result_lines:
        print(line)


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
    file_path = os.path.join(dir_path + "/data/names.json")
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
