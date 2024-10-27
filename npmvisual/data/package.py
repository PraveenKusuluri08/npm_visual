import pprint
from dataclasses import dataclass
from typing import Dict

from neo4j._data import Record

from npmvisual.data.dependency import Dependency


@dataclass
class Package:
    id: str
    latest_version: str
    dependencies: list[Dependency]
    description: str = ""

    @staticmethod
    def from_db_record(r: Record, dependencies: list[Dependency]):
        print("00000000000000000000000000000000000000000000000000000000000")
        print(r)
        pprint.pp(r)
        from_db = r["p"]
        # for d in dependencies:
        #     dependencies[] = ''

        p = Package(
            id=from_db.package_id,
            description=from_db.description,
            latest_version=from_db.latest_version,
            dependencies=dependencies,
        )
        return p
