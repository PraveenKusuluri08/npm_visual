from typing import Optional

from neomodel import (
    ArrayProperty,
    BooleanProperty,
    JSONProperty,
    RelationshipTo,
    StringProperty,
    StructuredNode,
)

from npmvisual._models.packument import Packument


class PackageNode(StructuredNode):
    """
    This is the Neomodel equivalent of the Pydantic Packument class.
    """

    # Core fields from the Packument

    id = StringProperty(unique_index=True, required=True)
    rev = StringProperty(required=True)
    time = JSONProperty()  # A dictionary-like field for 'time'

    # Optional fields
    cached = BooleanProperty(required=False)  # Optional boolean field
    dist_tags = JSONProperty()  # Dist-tags field as a dictionary
    users = JSONProperty(required=False)  # Users field, optional, stored as a dict

    # Hoisted fields from latest PackumentVersion
    name = StringProperty(required=True)
    git_head = StringProperty(required=False, alias="gitHead")

    # Additional optional fields
    readme = StringProperty(required=False)
    readme_filename = StringProperty(required=False, alias="readmeFilename")
    description = StringProperty(required=False)
    homepage = StringProperty(required=False)
    keywords = ArrayProperty(StringProperty, required=False)  # List of strings
    license = StringProperty(required=False)

    def __init__(self, packument: Packument):
        """
        Initialize a PackageNode from a Packument Pydantic instance.
        """
        # Map fields from the Packument class to the PackageNode
        self.id = packument.id
        self.rev = packument.rev
        self.time = packument.time
        self.cached = packument.cached
        self.dist_tags = packument.dist_tags
        self.users = packument.users
        self.name = packument.name
        self.git_head = packument.git_head
        self.readme = packument.readme
        self.readme_filename = packument.readme_filename
        self.description = packument.description
        self.homepage = packument.homepage
        self.keywords = packument.keywords
        self.license = packument.license
