import re
import shutil

from pydantic import BaseModel


class NSPrettyPrintable:
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
                value = NSPrettyPrintable.format_string(
                    value, len(level_indent + attr) + 2
                )
                output += f"{level_indent}{attr}: {value}\n"

            elif isinstance(value, list):
                output += f"{level_indent}{attr}:\n"
                output += NSPrettyPrintable.format_list(attr, value, level, indent)
            elif isinstance(value, dict):
                output += f"{level_indent}{attr}:\n"
                output += NSPrettyPrintable.format_dict(value, level, indent)
            elif isinstance(value, NSPrettyPrintable):
                output += f"{level_indent}{attr}:\n"
                output += value.to_readable_str(level + 1)
            else:
                output += f"{level_indent}{attr}: {value}\n"

        return output

    @staticmethod
    def format_list(
        attr: str,
        value: list,
        level: int,
        indent: str,
    ):
        output = ""
        for count, item in enumerate(value):
            if isinstance(item, NSPrettyPrintable):
                output += item.to_readable_str(level + 1)
                if (
                    NSPrettyPrintable.is_multiline_string(output)
                    and count != len(value) - 1
                ):
                    output += f"{indent*level}{indent},\n"
            elif isinstance(item, str):
                output += f"{indent*level}{NSPrettyPrintable.format_string(item, len(indent*level + attr) + 2)}\n"
            else:
                output += f"{indent*level}{item}"
        return output

    @staticmethod
    def format_dict(
        value: dict,
        level: int,
        indent: str,
    ):
        output = ""
        for key, val in value.items():
            if isinstance(val, NSPrettyPrintable):
                # output += f"{indent}{key} \n"
                output += val.to_readable_str(level + 1)
            else:
                output += f"{indent*(level+1)}{key}: {val}\n"
        return output

    def pretty_print(self):
        print(self.to_readable_str())

    @staticmethod
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

    @staticmethod
    def is_multiline_string(value: str) -> bool:
        """Returns True if the string will appear on more than one line in the terminal."""
        return "\n" in value

    @staticmethod
    def format_string(readme: str | None, size_of_other_chars_on_line: int = 0) -> str:
        """Formats the readme field to be a one-liner with special characters cleaned up."""
        if not readme:
            return "N/A"
        readme = NSPrettyPrintable._trim_string_with_ellipsis(
            readme, NSPrettyPrintable.get_terminal_width() - size_of_other_chars_on_line
        )
        return NSPrettyPrintable.clean_special_characters(readme)

    @staticmethod
    def _trim_string_with_ellipsis(input_string: str, max_length: int = 80) -> str:
        """Trims long strings with an ellipsis to fit the max length."""
        if len(input_string) > max_length:
            return input_string[: max_length - 3] + "..."
        return input_string

    @staticmethod
    def get_terminal_width() -> int:
        """Returns the width of the terminal, defaulting to 80 characters."""
        width = shutil.get_terminal_size((80, 20)).columns
        return width

    #     for attr, value in self.__dict__.items():
    #         if value is None:
    #             continue
    #         elif isinstance(value, str):
    #             output += NSBaseModel.format_string(value, len(level_indent + attr) + 2)
    #             output += f"{level_indent}{attr}: {value}\n"
    #         elif isinstance(value, list):
    #             output += f"{level_indent}{attr}:\n"
    #             output += NSBaseModel.format_list(attr, value, level, indent)
    #         elif isinstance(value, dict):
    #             output += f"{level_indent}{attr}:\n"
    #             output += NSBaseModel.format_dict(value, level, indent)
    #         elif isinstance(value, NSBaseModel):
    #             output += f"{level_indent}{attr}:\n"
    #             output += value.to_readable_str(level + 1)
    #         else:
    #             output += f"{level_indent}{attr}: {value}\n"
    #
    #     return output
    #
    # @staticmethod
    # def format_list(
    #     attr: str,
    #     value: list,
    #     level: int,
    #     indent: str,
    # ):
    #     output = ""
    #     for count, item in enumerate(value):
    #         if isinstance(item, NSBaseModel):
    #             output = item.to_readable_str(level + 1)
    #             if NSBaseModel.is_multiline_string(output) and count != len(value) - 1:
    #                 output += f"{indent*level}{indent},\n"
    #         elif isinstance(item, str):
    #             output = f"{indent*level}{NSBaseModel.format_string(item, len(indent*level + attr) + 2)}\n"
    #         else:
    #             output = f"{indent*level}{item}"
    #     return output
    #
    # @staticmethod
    # def format_dict(
    #     value: dict,
    #     level: int,
    #     indent: str,
    # ):
    #     output = ""
    #     for key, val in value.items():
    #         if isinstance(val, NSBaseModel):
    #             # output += f"{indent}{key} \n"
    #             output += val.to_readable_str(level + 1)
    #         else:
    #             output += f"{indent*(level+1)}{key}: {val}\n"
    #     return output
    #
    #
