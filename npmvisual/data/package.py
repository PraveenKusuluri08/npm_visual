import pprint
from dataclasses import dataclass
from typing import Dict

from neo4j._data import Record

from npmvisual.data.dependency import Dependency


@dataclass
class Package:
    id: str
    description: str
    latest_version: str
    dependencies: list[Dependency]

    @staticmethod
    def from_package_json(r_dict):
        id = r_dict.get("_id")
        description = r_dict.get("description")
        latest_version = r_dict.get("dist-tags", {}).get("latest")

        # some packages have no dependencies. represent this as an empty dict
        dependency_dict: Dict[str, str] = (
            r_dict.get("versions", {}).get(latest_version, {}).get("dependencies", {})
        )
        dependencies: list[Dependency] = []
        for package, version in dependency_dict.items():
            dependencies.append(Dependency(package, version))
        # print(f"dependencies = {dependencies}")
        return Package(id, description, latest_version, dependencies)

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
