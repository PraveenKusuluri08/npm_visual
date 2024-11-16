from dataclasses import dataclass
from typing import Any


class NSType:
    all_types: dict[str, "NSType"] = {}
    count: int = 0
    alias: str | None
    id: str
    id_pretty: str
    children: dict["str", "NSType"] | None = None
    self_type: str
    attrs: list[str] = []

    def __init__(self, t: Any):
        self.self_type = type(t).__name__
        id_pretty = ""

        if NSType.is_primitive(t):
            self.id = self.self_type
            id_pretty = self.self_type

        elif isinstance(t, list):
            self.children = {str(k): NSType(v) for k, v in enumerate(t)}
            child_ids = ""
            next(iter(self.children))
            if self.children:
                child_ids = list(self.children.values())[0].self_type
            self.id = f"list[{child_ids}]"
            self.id_pretty = f"\nlist[{child_ids}]\n"

        elif isinstance(t, dict):
            self.children = {k: NSType(v) for k, v in t.items()}
            id = f"dict[str,{self.self_type}]{{"
            id_pretty = f"\ndict[str,{"????????????"}]\n{{"
            for key, val in self.children.items():
                self.attrs.append(key)
                id += f'("{key}",{val.id}),'
                child_str = f'\n("{key}",{val.id_pretty}),\n'
                if isinstance(val, dict):
                    child_str = "dddddddddddd" + child_str + "ddd9999999"
                    pass
                id_pretty = child_str
            if len(self.children):
                id = id[:-1]  # remove trailing comma
                id_pretty = id[:-3]  # remove trailing comma and \n
                id += "}"
                id_pretty += "\n}"
            self.id = id
        else:
            raise TypeError(f"Unknown type: {type(t).__name__} (value: {t})")

        self.id_pretty = id_pretty
        self.count += 1
        NSType.all_types[self.id] = self

    def is_leaf(self):
        return self.children is None

    @staticmethod
    def is_primitive(obj):
        return isinstance(obj, int | float | bool | str | bytes | type(None))


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

    for t in NSType.all_types.values():
        print("---" * 44)
        print(t.id_pretty)
        print(t.id)


if __name__ == "__main__":
    test_nstype(input_data)
