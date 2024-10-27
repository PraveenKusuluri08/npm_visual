from dataclasses import dataclass
from typing import Dict

from flask import current_app as app
from neo4j._data import Record
from neo4j._sync.work.transaction import ManagedTransaction

from npmvisual import db
from npmvisual.data import cache
from npmvisual.data.dependency import Dependency
from npmvisual.data.scraper import scrape_package_json


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
        print(f"dependencies = {dependencies}")
        return Package(id, description, latest_version, dependencies)

    # @staticmethod
    # def from_db_record(r: Record):
    #     dependencies: Dict [str, str]
    #     for d in dependencies:
    #         dependencies[] = ''
    #
    #     p = Package(
    #         id=r.package_id,
    #         description=r.description,
    #         latest_version=r.latest_version,
    #         dependencies = dependencies,
    #     )
    #     return Package(id,description,latest_version, dependencies)


def db_create_dependency(package_id: str, dependent_package_id: str):
    db.execute_write(
        lambda tx: tx.run(
            """
            MATCH (a {package_id: $a_id}), 
                  (b {package_id: $b_id})
            MERGE (a)-[r:DependsOn]->(b)
            ON CREATE SET 
                a.created = timestamp(),
                b.created = timestamp(),
                r.created = timestamp()
            ON MATCH SET
                a.counter = coalesce(a.counter, 0) + 1,
                a.accessTime = timestamp(),
                b.counter = coalesce(a.counter, 0) + 1,
                b.accessTime = timestamp(),
                r.counter = coalesce(a.counter, 0) + 1,
                r.accessTime = timestamp()
            """,
            a_id=package_id,
            b_id=dependent_package_id,
        )
    )


def db_merge_package_and_dependents(package: Package):
    # create or update package in db if it does not already exist
    db_merge_package(package)

    for p in package.dependencies:
        db_create_dependency(package.id, p.package)


def db_merge_package_id_only(package: Package):
    """Add package to db if it does not exist"""
    db.execute_write(
        lambda tx: tx.run(
            """
            MERGE (p:Package {
                package_id: $package_id
            })
            ON CREATE SET p.created = timestamp()
            ON MATCH SET
            p.counter = coalesce(p.counter, 0) + 1,
            p.accessTime = timestamp()
            """,
            package_id=package.id,
        )
    )


def db_merge_package(package: Package):
    """Add package to db if it does not exist, update otherwise"""
    db.execute_write(
        lambda tx: tx.run(
            """
            MERGE (p:Package {
                package_id: $package_id,
                description: $description,
                latest_version: $latest_version
            })
            ON CREATE SET p.created = timestamp()
            ON MATCH SET
            p.counter = coalesce(p.counter, 0) + 1,
            p.accessTime = timestamp()
            """,
            package_id=package.id,
            description=package.description,
            latest_version=package.latest_version,
        )
    )


def _get_package_from_db(package_name: str) -> Package | None:
    print(f"searching for package in db: {package_name}")

    def match_package_tx(
        tx: ManagedTransaction,
        package_id: str,
    ):
        result = tx.run(
            """
            MATCH (p:Package)
            WHERE p.package_id = $package_id
            RETURN p
            """,
            package_id=package_id,
        )
        return result.single()

    x = db.execute_read(match_package_tx, package_name)
    print(f"x={x}")
    return


def _get_package_from_cache(package_name: str) -> Package | None:
    print(f"searching for package in cache: {package_name}")
    # app.logger.info(f"getting {package_name}")
    cache.clean_if_invalid(package_name)
    # print("diagnose1")
    # diagnose(package_name)
    if cache.exists(package_name):
        app.logger.info(f"{package_name} is cached")
        r_dict = cache.load(package_name)
        p = Package.from_package_json(r_dict)
        db_merge_package_and_dependents(p)
        return p
    return None


def _get_package_from_online(package_name: str) -> Package | None:
    app.logger.info(f"{package_name} is not cached. Scraping from online")
    r_dict = scrape_package_json(package_name)

    if r_dict is not None:
        cache.save(package_name, r_dict)
        p = Package.from_package_json(r_dict)
        db_merge_package_and_dependents(p)
        return p
    # print("diagnose2")
    # diagnose(package_name)
    print(f"Failed to scrape {package_name}")


def get_package(package_name: str) -> Package | None:
    print(f"searching for package: {package_name}")
    p = _get_package_from_db(package_name)
    if p is not None:
        print("getPackage3")
        return p

    p = _get_package_from_cache(package_name)

    print("getPackage5")
    if p is not None:
        print("getPackage6")
        return p

    print("getPackage7")
    p = _get_package_from_online(package_name)


def validate(r_dict):
    pass


def update_all():
    pass

    # def find(self):
    #     package = graph.find_one("package", "id", self.id)
    #     return package
    #
    # def register(self):
    #     if not self.find():
    #         package = Node("Package", id=self.id, description="testing")
    #         graph.create(package)
    #         return True
    #     else:
    #         return False

    # def __init__(self, fname):
    # dict.__init__(self, fname=fname)
