from pydantic import BaseModel
from typing import Any


class NSBaseModel(BaseModel):
    """
    A base class that provides the `prettyPrint` method for pretty-printing any Pydantic model.
    All child models should inherit from this class to use the `prettyPrint` method.
    """

        def _trim_string_with_ellipsis(input_string: str, max_length: int) -> str:
            if len(input_string) > max_length:
                return input_string[: max_length - 3] + "..."
            return input_string

        # Start building the string with class name
        strBuilder = f"  {self.__class__.__name__}:\n"

        # Try to get 'id' or '_id' and fall back on '_id' if 'id' does not exist
        id_value = getattr(self, "id", None) or getattr(self, "_id", None)
        if id_value:
            strBuilder += f"     id: {id_value}\n"

        # Loop through attributes
        for var, value in self.model_dump().items():
            if isinstance(value, str):
                value = _trim_string_with_ellipsis(value, 44)
            strBuilder += f"     {var}: {value}\n"

        print(strBuilder)
