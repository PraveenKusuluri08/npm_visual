import itertools
import string
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

from npmvisual._models.ns_pretty_printable import NSPrettyPrintable

COUNT = 1


class NSType:
    alias: str | None
    structure: str
    id_pretty: str
    children: dict["str", "NSType"] | None = None
    self_type: str
    attrs: list[str] = []

    def __init__(self, t: Any):
        self.self_type = type(t).__name__

        # _pretty_print_type_structure(t)
        # global COUNT
        # print(f"\n\n\ninit of NSType. {self.self_type} count ={COUNT}")
        # COUNT += 1
        id_pretty = ""

        if NSType.is_primitive(t):
            self.structure = self.self_type

            id_pretty = self.self_type

        elif isinstance(t, list):
            # for k in t:
            # print(f"nsType dict children: {k}")
            self.children = {str(k): NSType(v) for k, v in enumerate(t)}
            child_structures = ""
            if self.children:
                child_structures = list(self.children.values())[0].self_type
            self.structure = f"list[{child_structures}]"
            self.structure_pretty = f"\nlist[{child_structures}]\n"

        elif isinstance(t, dict):
            # for k, v in t.items():
            #     if isinstance(v, str):
            #         print(
            #             f"nsType dict children: {k} {NSPrettyPrintable.format_string(v, 100)}"
            #         )
            #     else:
            #         print(f"nsType dict children: {k} {v}")
            self.children = {k: NSType(v) for k, v in t.items()}
            structure = f"dict[str,{self.self_type}]{{"
            id_pretty = f"\ndict[str,{"????????????"}]\n{{"
            for key, val in self.children.items():
                self.attrs.append(key)
                structure += f'("{key}",{val.structure}),'
                child_str = f'\n("{key}",{val.id_pretty}),\n'
                if isinstance(val, dict):
                    child_str = "dddddddddddd" + child_str + "ddd9999999"
                    pass
                id_pretty = child_str
            if len(self.children):
                structure = structure[:-1]  # remove trailing comma
                id_pretty = structure[:-3]  # remove trailing comma and \n
                structure += "}"
                id_pretty += "\n}"
            self.structure = structure

        else:
            raise TypeError(f"Unknown type: {type(t).__name__} (value: {t})")
        self.structure_pretty = id_pretty

        NSTypeDB.add(self)

    def is_leaf(self):
        return self.children is None

    @staticmethod
    def is_primitive(obj):
        return isinstance(obj, int | float | bool | str | bytes | type(None))


@dataclass
class NSTypeCount:
    nstype: NSType
    count = 1


class NSTypeDB:
    _instance = None  # Class variable to hold the single instance
    all_types: dict[str, NSTypeCount] = {}

    def __new__(cls, *args, **kwargs):
        # Check if an instance already exists
        if cls._instance is None:
            # If not, create it and store in _instance
            cls._instance = super(NSTypeDB, cls).__new__(cls)
        return cls._instance

    @classmethod
    def add(cls, unknown_type: NSType):
        if len(cls.all_types) > 1000:
            cls.print()
            raise Exception("terminating for testing purposes")

        if unknown_type.structure in cls.all_types:
            cls.all_types[unknown_type.structure].count += 1
        else:
            cls.all_types[unknown_type.structure] = NSTypeCount(unknown_type)

    @classmethod
    def print(cls):
        print("===" * 44)
        print("===" * 44)
        print("===" * 44)
        sorted_types = sorted(cls.all_types.values(), key=lambda t: t.count, reverse=True)
        for t in sorted_types:
            if t.count > 1:
                print(f"count={t.count} {t.nstype.structure}")
        print("===" * 44)
        print("===" * 44)
        print("===" * 44)


def _pretty_print_type_structure(data: Any, indent: int = 0):
    # Helper function to format and print the data recursively
    space = " " * indent
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{space}{key}:")
            _pretty_print_type_structure(value, indent + 2)

    elif isinstance(data, list):
        for index, item in enumerate(data):
            print(f"{space}- Item {index + 1}:")
            _pretty_print_type_structure(item, indent + 2)

    elif isinstance(data, str):
        print(f"{space}- {NSPrettyPrintable.format_string(data, 100)}")
    else:
        # Print the type for primitive values
        print(f"{space}- {data}")


def _get_type_structure(data: dict[str, Any]):
    def recursive_type_structure(value: Any) -> Any:
        if isinstance(value, dict):
            # Recurse into a dictionary and apply recursively to each key-value pair
            return {k: recursive_type_structure(v) for k, v in value.items()}

        elif isinstance(value, list):
            # Process each element in the list and return a list of types
            return [recursive_type_structure(v) for v in value]

        else:
            # Return the type of the value if it's a primitive or object type
            return [type(value).__name__]

    if data and data.items():
        return {k: recursive_type_structure(v) for k, v in data.items()}
    else:
        print(f"???????????????????????{data}")


def _print_json_variable(json_dict):
    some_key = "could not find"
    some_key = json_dict.get("license")
    print(some_key)
    versions: dict[str, Any] = json_dict.get("versions")  # type: ignore
    vers_tag = None  # "3.0.0"
    # print(versions[vers_tag])
    if versions and vers_tag and versions[vers_tag]:
        # if versions and len(versions) > 0:
        last_item = versions[vers_tag]  # Any = sorted(versions.items())[-1][1]
        some_key = last_item.get("contributors")
        # structure = _get_type_structure(some_key)
        # _pretty_print_type_structure(structure)
        # nsprint(
        #     f"some_key:{some_key}",
        # )
    print(f"\nkey: {some_key}\n")


input_data = {
    "name": "Alice",
    "age": 30,
    "is_student": False,
    "grades": [90, 85, 92],
    "address": {"city": "Wonderland", "zip": "12345"},
    "hobbies": None,
    "scores": {"math": 95, "science": 88},
}


# Testing function
def test_nstype(input_data):
    print("Testing NSType with the following input data:")
    print(input_data)
    print("\nCreating NSType instance...\n")

    # Create an NSType instance
    nstype_instance = NSType(input_data)

    # Print the NSType instance
    print("NSType instance:")
    print(nstype_instance)

    # Print the shared first_instance_data
    print("\nAll Types:")
    NSTypeDB.print()


class AliasGenerator:
    _instance = None  # This will hold the single instance of the class
    _counter = 0  # Counter to track the number of generated aliases
    _alias_dict = {}  # Dictionary to store alias and count mappings

    def __new__(cls):
        """
        Singleton pattern: Ensure only one instance of AliasGenerator is created.
        """
        if cls._instance is None:
            cls._instance = super(AliasGenerator, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize the alias generator. This will run only once due to the Singleton pattern.
        """
        # Initialize variables if this is the first instance
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._length = 1  # Start generating strings from length 1
            self._alphabet = string.ascii_lowercase  # a-z

    def generate_unique_string(self):
        """
        Generates a unique alias string based on the current counter.

        Returns:
            str: A unique alias.
        """
        # Increment the counter
        self._counter += 1

        # Generate alias string corresponding to the current counter
        alias = self._get_alias_from_counter(self._counter)

        # Add the alias and count to the dictionary
        self._alias_dict[alias] = self._counter

        return alias

    def _get_alias_from_counter(self, counter):
        """
        Generates a unique alias string from a counter value.

        Args:
            counter (int): The current counter value to convert into an alias.

        Returns:
            str: The alias corresponding to the counter.
        """
        # Start with single-letter strings, then generate multi-letter strings
        length = 1
        while True:
            total_combinations = len(self._alphabet) ** length
            if counter <= total_combinations:
                return self._generate_alias_of_length(length, counter - 1)
            counter -= total_combinations
            length += 1

    def _generate_alias_of_length(self, length, counter):
        """
        Generates an alias of the given length from the alphabet using the counter value.

        Args:
            length (int): The length of the alias.
            counter (int): The current counter value used to generate the alias.

        Returns:
            str: The alias of the specified length.
        """
        # Generate the alias using the counter in a base-26 system (a=0, b=1, ..., z=25)
        alias = []
        for i in range(length):
            alias.append(self._alphabet[counter % len(self._alphabet)])
            counter //= len(self._alphabet)

        return "".join(reversed(alias))

    def get_all_aliases(self):
        """
        Returns the dictionary of generated aliases with their counts.

        Returns:
            dict: A dictionary mapping alias strings to their respective counts.
        """
        return self._alias_dict


# Example usage
def test_alias_generator():
    generator = AliasGenerator()

    # Generate a few aliases and print them
    for _ in range(20):  # Generate 20 aliases
        alias = generator.generate_unique_string()
        print(f"Alias: {alias}, Count: {generator._counter}")

    # Print the entire dictionary of aliases
    print("\nAll Generated Aliases:")
    print(generator.get_all_aliases())


# Run the example usage
test_alias_generator()
if __name__ == "__main__":
    test_nstype(input_data)
