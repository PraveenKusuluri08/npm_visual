from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from npmvisual.models import Dependency


# Define Package class (forbid extra fields)
class Package:
    id: str = Field(..., alias="_id")  # Map _id in input to id in the model
    description: str
    dependencies: list[Dependency]
    latest_version: str
    # dist_tags: Dist_Tags

    class Config:
        extra = "forbid"  # Forbid extra fields
        allow_population_by_field_name = (
            True  # Allow using field names in the model (like `id`)
        )

    # Optional: Override the default __init__ method to handle manual initialization
    def __init__(self, **data):
        # Manually handle the 'dependencies' field, initialize it separately
        # dependencies = data.pop('dependencies', None)  # Pop dependencies out of data
        super().__init__(**data)  # Call the parent constructor to initialize other fields
        # some packages have no dependencies. represent this as an empty dict
        dependency_dict: dict[str, str] = (
            data.get("versions", {}).get("latest_version", {}).get("dependencies", {})
        )
        dependencies: list[Dependency] = []
        for package, version in dependency_dict.items():
            dependencies.append(Dependency(package, version))
        self.dependencies = dependencies

    @classmethod
    def to_Package(cls):
        pass


# Function to create a Package from a JSON string (no extra fields allowed)
def package_from_json(json_data: dict[str, Any]) -> Package | None:
    try:
        return Package.model_validate(
            json_data
        )  # Parse the dictionary into a Package object
    except ValidationError as e:
        print(f"Validation error: {e}")
        return None


def prettyPrint(package: Package):
    def _trim_string_with_ellipsis(input_string: str, max_length: int) -> str:
        if len(input_string) > max_length:
            return input_string[: max_length - 3] + "..."  # Leave space for the ellipsis
        return input_string

    strBuilder = f"  Package: \t{package.id}\n"
    for (
        var,
        value,
    ) in package.model_dump().items():  # Use .items() to iterate over key-value pairs
        if isinstance(value, str):
            value = _trim_string_with_ellipsis(value, 44)
        strBuilder += f"     {var}: {value}\n"  # Convert value to string and format
    print(strBuilder)


#
#
def json_to_package(json_data) -> Package:
    # some packages have no dependencies. represent this as an empty dict
    dependency_dict: dict[str, str] = (
        json_data.get("versions", {}).get("latest_version", {}).get("dependencies", {})
    )
    dependencies: list[Dependency] = []
    for package, version in dependency_dict.items():
        dependencies.append(Dependency(package, version))

    p = Package(
        id=json_data.get("_id"),
        latest_version=json_data.get("latest_version"),
        description=json_data.get("description"),
        dependencies=dependencies,
    )

    # optional tags
    # print("0----------------")
    # print(r_dict)
    # print("1----------------")
    # Parse and validate the data using Pydantic

    dt_r_dict = json_data.get("dist-tags")
    print(f"dt_r_dict={dt_r_dict}")
    # try:
    #     # dt = Dist_Tags(**dt_r_dict)  # Pydantic will validate the data here
    #     # print(person.dict())  # This will output a validated dictionary
    #     print(f"dt={dt}")
    #     p["dist_tags"] = dt
    # except ValidationError as e:
    #     print(f"Validation error: {e}")

    # dt:Dist_Tags = {}
    #  dt_r_dict["latest"]
    #
    # for var_name, var_type in Dist_Tags.__annotations__.items():
    #
    #     print(f"Variable name: {var_name}, Type: {var_type}")
    # # print(f"dt={dt}")
    return p


#
# def to_dict(self):
#     return {
#         "id": self.id,
#         "latest_version": self.latest_version,
#         "description": self.description,
#         "dependencies": [
#             dep.to_dict() for dep in self.dependencies
#         ],  # convert dependencies to dicts
#     }
#
# @staticmethod
# def from_db_record(r: record, dependencies: list[dependency]) -> package:
#     from_db = r["p"]
#     p = package(
#         id=from_db.package_id,
#         description=from_db.description,
#         latest_version=from_db.latest_version,
#         dependencies=dependencies,
#         dist_tags=from_db["dist-tags"],
#     )
#     return p
#
# @staticmethod
# def from_json(r_dict) -> package:
#     id = r_dict.get("_id")
#     description = r_dict.get("description")
#     latest_version = r_dict.get("dist-tags", {}).get("latest")
#     if not description:
#             description = ""
#         assert id is not None
#
#         # some packages have no dependencies. represent this as an empty dict
#         dependency_dict: dict[str, str] = (
#             r_dict.get("versions", {}).get(latest_version, {}).get("dependencies", {})
#         )
#         dependencies: list[Dependency] = []
#         for package, version in dependency_dict.items():
#             dependencies.append(Dependency(package, version))
#
#
#         dist_tags = r_dict.get("dist-tags")
#
#         return Package(
#             id,
#             latest_version,
#             dependencies,
#             description,
#         )
