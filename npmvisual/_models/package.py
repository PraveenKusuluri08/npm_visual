from dataclasses import dataclass
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

"""Increment this and run a migration whenever you change the schema"""
SCHEMA_VERSION = 1


@dataclass
class PackageData:
    package: "Package"
    dependencies: dict[str, str]


class DependencyRel(StructuredRel):
    version = StringProperty(required=True)


# class DIInfo:
#     my_datetime = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class Package(StructuredNode, NSPrettyPrintable):
    """
    This is the Neomodel equivalent of the Pydantic Packument class.
    """

    SCRAPE_STATUS_CHOICES = {
        "full": "fully_scraped",
        "part": "partially_scraped",
        "id_only": "not_yet_scraped",
    }

    di_schema_version = IntegerProperty(required=True, index=True)
    di_created_at = DateTimeProperty(required=True)
    di_fully_scraped_at = DateTimeProperty(index=True)
    di_scrape_status = StringProperty(
        required=True, choices=SCRAPE_STATUS_CHOICES, index=True
    )

    package_id: str = StringProperty(unique_index=True, required=True)  # type: ignore
    time = JSONProperty()

    # Optional fields
    cached = BooleanProperty(required=False)
    dist_tags = JSONProperty()
    users = JSONProperty(required=False)

    # Hoisted fields from latest PackumentVersion
    name = StringProperty(required=False)
    git_head = StringProperty(required=False)

    readme = StringProperty(required=False)
    readme_filename = StringProperty(required=False)
    description = StringProperty(required=False)
    homepage = StringProperty(required=False)
    keywords = ArrayProperty(StringProperty(), required=False)
    license = StringProperty(required=False)

    # dependency_id_dict: dict[str, str] = ArrayProperty(StringProperty(), required=True)  # type: ignore
    dependencies = RelationshipTo(
        "Package", "DEPENDS_ON", cardinality=ZeroOrMore, model=DependencyRel
    )

    def __str__(self):
        return f"{self.__class__.__name__} (id={self.package_id})"

    def id_attr(self) -> str:
        return "package_id"

    @classmethod
    def from_packument(cls, packument: Packument) -> PackageData:
        version = packument.get_latest_version()
        if not version:
            raise Exception("no latest version")
        dependency_id_dict = packument.get_dependencies(version)
        assert dependency_id_dict is not None

        return PackageData(
            package=cls(
                package_id=packument.id,
                di_schema_version=SCHEMA_VERSION,
                di_created_at=datetime.datetime.now(pytz.utc),
                di_fully_scraped_at=datetime.datetime.now(pytz.utc),
                di_scrape_status="full",
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
            ),
            dependencies=dependency_id_dict,
        )

    @classmethod
    def create_placeholder(cls, package_id: str) -> PackageData:
        """If for whatever reason, you can't scrape the data from online, or if something
        went wrong, use this as a temporary value so that the relationships still work.
        things that depend on this still will point to something."""

        return PackageData(
            package=cls(
                package_id=package_id,
                di_created_at=datetime.datetime.now(pytz.utc),
                di_schema_version=SCHEMA_VERSION,
                di_scrape_status="id_only",
            ),
            dependencies={},
        )

    def pre_save(self):
        """Save hooks are called regardless of wether the node is new or not. To
        determine if a node exists in pre_save, check for an id attribute on self."""
        if self.package_id and self.di_scrape_status == "full":
            self.di_fully_scraped_at = datetime.datetime.now(pytz.utc)
