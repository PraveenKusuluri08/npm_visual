import hashlib
import json
import os
import shutil
from typing import TypeVar, Iterable, override
import random

T = TypeVar("T")


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

    @override
    def __repr__(self):
        return "Infinity"


# Singleton instance of Infinity
infinity = Infinity()


def get_all_package_names(limit: int = 300, offset: int | None = None) -> set[str]:
    names: set[str] = set()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "data/names.json")

    # Open the file and load the JSON data into memory
    with open(file_path) as file:
        data: list[str] = json.load(file)

    # Get the total number of elements in the data
    num_lines = len(data)

    if offset is None:
        offset = random.randint(0, max(num_lines - limit, 0))

    # Slice the data to get the subset of names starting at random_offset
    selected_names = data[offset : offset + limit]

    # Add selected names to the set
    names.update(selected_names)

    # Print information about the set
    print(f"Created a set of all package names with {len(names)} elements.")

    return names


def find_duplicates(lst: Iterable[T]) -> set[T]:
    seen: set[T] = set()
    duplicates: set[T] = set()
    for item in lst:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)

    return duplicates
