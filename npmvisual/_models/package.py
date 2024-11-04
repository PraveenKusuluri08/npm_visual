# import pprint
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
    def from_db_record(r: Record, dependencies: list[Dependency]):
        from_db = r["p"]
        p = Package(
            id=from_db.package_id,
            description=from_db.description,
            latest_version=from_db.latest_version,
            dependencies=dependencies,
        )
        return p
