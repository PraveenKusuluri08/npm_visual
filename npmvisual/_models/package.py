# import pprint
from __future__ import annotations
from dataclasses import dataclass

from neo4j._data import Record

from npmvisual.models import Dependency


@dataclass
class Package:
    id: str
    latest_version: str
    dependencies: list[Dependency]
    description: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "latest_version": self.latest_version,
            "description": self.description,
            "dependencies": [
                dep.to_dict() for dep in self.dependencies
            ],  # Convert dependencies to dicts
        }

    @staticmethod
    def from_db_record(r: Record, dependencies: list[Dependency]) -> Package:
        from_db = r["p"]
        p = Package(
            id=from_db.package_id,
            description=from_db.description,
            latest_version=from_db.latest_version,
            dependencies=dependencies,
        )
        return p

    @staticmethod
    def from_json(r_dict) -> Package:
        id = r_dict.get("_id")
        description = r_dict.get("description")
        latest_version = r_dict.get("dist-tags", {}).get("latest")
        if not description:
            description = ""
        assert id is not None

        # some packages have no dependencies. represent this as an empty dict
        dependency_dict: dict[str, str] = (
            r_dict.get("versions", {}).get(latest_version, {}).get("dependencies", {})
        )
        dependencies: list[Dependency] = []
        for package, version in dependency_dict.items():
            dependencies.append(Dependency(package, version))
        return Package(
            id,
            latest_version,
            dependencies,
            description,
        )
