from logging import error
from typing import Optional

from neomodel import (
    ArrayProperty,
    BooleanProperty,
    JSONProperty,
    RelationshipTo,
    StringProperty,
    StructuredNode,
)
from neomodel.sync_.relationship_manager import ZeroOrMore

from npmvisual._models.ns_base_model import NSPrettyPrintable
from npmvisual._models.packument import Packument


class PackageNode(StructuredNode, NSPrettyPrintable):
    """
    This is the Neomodel equivalent of the Pydantic Packument class.
    """

    package_id: str = StringProperty(unique_index=True, required=True)  # type: ignore
    rev = StringProperty(required=True)
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

    dependency_id_list: list[str] | None = ArrayProperty(StringProperty(), required=False)  # type: ignore
    dependencies = RelationshipTo("PackageNode", "DEPENDS_ON", cardinality=ZeroOrMore)

    @classmethod
    def from_packument(cls, packument: Packument):
        version = packument.get_latest_version()
        if not version:
            raise Exception("no latest version")
        dependency_id_list = packument.get_dependencies(version)
        print(f"dependency_id_list={dependency_id_list}")
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
            dependency_id_list=dependency_id_list,
        )  # def save(self, **kwargs):

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
