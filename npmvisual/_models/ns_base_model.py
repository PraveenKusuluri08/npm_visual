import re
import shutil

from pydantic import BaseModel


class NSBaseModel(BaseModel):
    """
    A base class that provides the `prettyPrint` method for pretty-printing any Pydantic model.
    All child models should inherit from this class to use the `prettyPrint` method.
    """

    def to_readable_str(self, level=1, indent="    "):
        """
        A generic method to convert the model's attributes to a readable string.
        Allows children to override this method for custom formatting.
        """
        # Determine the indentation based on the level
        level_indent = indent * level
        # output = f"{indent}{self.__class__.__name__}:\n"
        output = ""

        # Iterate over the attributes in the object
        for attr, value in self.__dict__.items():
            if value is None:  # Skip None values
                continue

            elif isinstance(value, str):
                value = format_string(value, len(level_indent + attr) + 2)
                output += f"{level_indent}{attr}: {value}\n"

            # Handle lists: print each item on a new line with an extra tab
            elif isinstance(value, list):
                # output += f"{indent}---------- start of list[NSBaseModel] indent={indent}, level={level} ----------------------\n"
                output += f"{level_indent}{attr}:\n"
                for count, item in enumerate(value):
                    if isinstance(item, NSBaseModel):
                        item_output = item.to_readable_str(level + 1)
                        if is_multiline_string(item_output) and count != len(value) - 1:
                            item_output += f"{level_indent}{indent},\n"
                    elif isinstance(item, str):
                        item_output = f"{level_indent}{format_string(item, len(level_indent + attr) + 2)}\n"
                    else:
                        item_output = f"{level_indent}{item}"
                    output += item_output
                # output += f"{indent}---------- end of list[NSBaseModel] ----------------------\n"

            # Handle dicts: print each key-value pair on a new line with an extra tab
            elif isinstance(value, dict):
                # output += f"{indent}---------- start of dict[Any, NSBaseModel] indent={indent}, level={level} ----------------------\n"
                output += f"{level_indent}{attr}:\n"
                for key, val in value.items():
                    if isinstance(val, NSBaseModel):
                        # output += f"{indent}{key} \n"
                        output += val.to_readable_str(level + 1)
                    else:
                        output += f"{level_indent}{indent}{key}: {val}\n"
                # output += (
                #     f"{indent}---------- end of dict[Any, NSBaseModel] -------------\n"
                # )

            # Handle nested NSBaseModel instances
            elif isinstance(value, NSBaseModel):
                # output += f"{indent}---------- start of NSBaseModel indent={indent}, level={level} ----------------------\n"
                output += f"{level_indent}{attr}:\n"
                output += value.to_readable_str(level + 1)
                # output += f"{indent}-------- end of NSBaseModel ----------------------\n"

            # Handle other regular attributes (strings, integers, etc.)
            else:
                output += f"{level_indent}{attr}: {value}\n"

        return output

    def pretty_print(self):
        # print(self.to_pretty_string())
        print(self.to_readable_str())


def clean_special_characters(value: str) -> str:
    """Cleans special characters like \\n, \\t, \\r, and other control characters for better readability."""
    # Replace common escape sequences with labels
    value = value.replace("\\n", " \\n ")  # Show newline escape as a label
    value = value.replace("\\t", " \\t ")  # Show tab escape as a label
    value = value.replace("\\r", " \\r ")  # Show carriage return escape as a label
    value = value.replace("\\b", " \\b ")  # Show backspace escape as a label

    # Remove any other control characters (ASCII 0-31), except for common printable characters
    value = re.sub(
        r"[\x00-\x1F\x7F]", " ", value
    )  # Replace all control characters with spaces

    # Also remove any literal newlines or extra spaces at the beginning and end
    value = value.strip()

    # Ensure it is just one line by replacing multiple spaces/newlines with a single space
    value = re.sub(r"\s+", " ", value)

    return value


def is_multiline_string(value: str) -> bool:
    """Returns True if the string will appear on more than one line in the terminal."""
    return "\n" in value


def format_string(readme: str | None, size_of_other_chars_on_line: int = 0) -> str:
    """Formats the readme field to be a one-liner with special characters cleaned up."""
    if not readme:
        return "N/A"
    readme = _trim_string_with_ellipsis(
        readme, get_terminal_width() - size_of_other_chars_on_line
    )
    return clean_special_characters(readme)


def _trim_string_with_ellipsis(input_string: str, max_length: int = 80) -> str:
    """Trims long strings with an ellipsis to fit the max length."""
    if len(input_string) > max_length:
        return input_string[: max_length - 3] + "..."
    return input_string


def get_terminal_width() -> int:
    """Returns the width of the terminal, defaulting to 80 characters."""
    width = shutil.get_terminal_size((80, 20)).columns
    return width
