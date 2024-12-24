import datetime
from logging import error
from typing import Optional

from neomodel.properties import IntegerProperty
import pytz
from neomodel import (
    ArrayProperty,
    BooleanProperty,
    DateTimeProperty,
    JSONProperty,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    StructuredRel,
)
from neomodel.sync_.relationship_manager import ZeroOrMore

from npmvisual._models.ns_pretty_printable import NSPrettyPrintable
from npmvisual._models.packument import Packument


class DependencyRel(StructuredRel):
    version = StringProperty(required=True)


# class DIInfo:
#     my_datetime = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class Package(StructuredNode, NSPrettyPrintable):
    """
    This is the Neomodel equivalent of the Pydantic Packument class.
    """

    # UPDATE_STATUS_CHOICES = {
    #     "Full": "Fully_Updated",
    #     "Part": "Partially_Updated",
    # }
    #
    # di_version = IntegerProperty(required=True, default=1)
    # di_created_at = DateTimeProperty(required=True, default_now=True)
    # di_full_updated_at = DateTimeProperty(required=True, default_now=True)
    # di_update_status = StringProperty(required=True, choices=UPDATE_STATUS_CHOICES)

    package_id: str = StringProperty(unique_index=True, required=True)  # type: ignore
    time = JSONProperty()

    # Optional fields
    cached = BooleanProperty(required=False)
    dist_tags = JSONProperty()
    users = JSONProperty(required=False)

    # Hoisted fields from latest PackumentVersion
    name = StringProperty(required=True)
    git_head = StringProperty(required=False)

    readme = StringProperty(required=False)
    readme_filename = StringProperty(required=False)
    description = StringProperty(required=False)
    homepage = StringProperty(required=False)
    keywords = ArrayProperty(StringProperty(), required=False)
    license = StringProperty(required=False)

    dependency_id_dict: dict[str, str] = ArrayProperty(StringProperty(), required=True)  # type: ignore
    dependencies = RelationshipTo(
        "Package", "DEPENDS_ON", cardinality=ZeroOrMore, model=DependencyRel
    )

    def __str__(self):
        return f"{self.__class__.__name__} (id={self.package_id})"

    def id_attr(self) -> str:
        return "package_id"

    @classmethod
    def from_packument(cls, packument: Packument):
        version = packument.get_latest_version()
        if not version:
            raise Exception("no latest version")
        dependency_id_dict = packument.get_dependencies(version)
        assert dependency_id_dict is not None

        return cls(
            package_id=packument.id,
            rev=packument.rev,
            time=packument.time,
            cached=packument.cached,
            dist_tags=packument.dist_tags,
            users=packument.users,
            name=packument.name,
            git_head=packument.git_head,
            readme=packument.readme,
            readme_filename=packument.readme_filename,
            description=packument.description,
            homepage=packument.homepage,
            keywords=packument.keywords,
            license=packument.license,
            dependency_id_list=dependency_id_dict,
        )  # def save(self, **kwargs):

    def pre_save(self):
        """Save hooks are called regardless of wether the node is new or not. To
        determine if a node exists in pre_save, check for an id attribute on self."""
        if self.id:
            pass
            # self.di_updated_at = datetime.datetime.now(pytz.utc)

    # def connect_dependencies(self):
    #     # Loop over each package_id in the dependencies and connect it to the current package_node
    #     for dep_id in self.dependency_id_list.all():
    #         # Look up the PackageNode for the dependency by its package_id
    #         dependency_node = PackageNode.nodes.get_or_none(package_id=dep_id)
    #
    #         if dependency_node:
    #             # If the dependency node exists, connect it to the current package node
    #             dependency_node.dependencies.connect(dependency_node)
    #         else:
    #             # If the dependency node doesn't exist, we can either create it or handle it
    #             # Optionally, we could create a new node for the dependency if needed
    #             print(f"Dependency {dep_id} does not exist in the database.")
    #             # I might decide to create it, depending on your use case:
    #             # dependency_node = PackageNode(package_id=dep_id)
    #             # package_node.dependencies.connect(dependency_node)

    # Save the PackageNode after connecting dependencies
    # package_node.save()
    # return package_node

    #     """
    #     Override save method to ensure relationships are saved properly.
    #     """
    #     # Save the PackageNode instance first
    #     super().save(**kwargs)
    #
    #     # Then, connect the relationships (contributors, maintainers)
    #     for contributor in self.contributors:
    #         self.contributors.connect(contributor)
    #     for maintainer in self.maintainers:
    #         self.maintainers.connect(maintainer)
