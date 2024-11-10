from pydantic import BaseModel
from typing import Any


class NSBaseModel(BaseModel):
    """
    A base class that provides the `prettyPrint` method for pretty-printing any Pydantic model.
    All child models should inherit from this class to use the `prettyPrint` method.
    """

    def pretty_print(self):
        print(self.to_pretty_string())

    def to_pretty_string(self, indent_level: int = 0) -> str:
        def _trim_string_with_ellipsis(input_string: str, max_length: int) -> str:
            if len(input_string) > max_length:
                return input_string[: max_length - 3] + "..."
            return input_string

        def variable_to_pretty_string(variable, indent_level: int = 1) -> str:
            strBuilder = ""
            # Loop through attributes
            for var, value in variable.values():
                # If the value is a string, trim it to fit
                if isinstance(value, str):
                    value = _trim_string_with_ellipsis(value, 90)
                    strBuilder += f"{' ' * (indent_level + 4)}{var}: {value}\n"

                # If the value is a nested NSBaseModel, recursively call prettyPrint
                elif isinstance(value, NSBaseModel):
                    strBuilder += f"{' ' * (indent_level + 4)}{var}:\n"
                    # Recursively call prettyPrint with increased indentation
                    strBuilder += value.to_pretty_string(indent_level + 8)

                elif isinstance(value, dict | list):
                    strBuilder += variable_to_pretty_string(value, indent_level + 4)
                    pass
                else:
                    strBuilder += f"{' ' * (indent_level + 4)}{var}: {value}\n"
            return strBuilder

        # Start building the string with class name
        str_builder = f"{' ' * indent_level}{self.__class__.__name__}:\n"

        # Try to get 'id' or '_id' and fall back on '_id' if 'id' does not exist
        id_value = getattr(self, "id", None) or getattr(self, "_id", None)
        if id_value:
            str_builder += f"{' ' * (indent_level + 4)}id: {id_value}\n"

        str_builder += variable_to_pretty_string(self, indent_level + 1)
        return str_builder
