from typing import Dict, Set
from flask import current_app as app
from neo4j._sync.work.transaction import ManagedTransaction
from neo4j.graph import Node

from npmvisual import db
from npmvisual.data import cache
from npmvisual.data.db_dependency import db_dependency_merge, get_dependencies_from_db
from npmvisual.data.dependency import Dependency
from npmvisual.data.package import Package
from npmvisual.data.scraper import scrape_package_json


def db_package_get_all() -> list[Package]:
    def get_packages_tx(tx):
        result = tx.run(
            """
            MATCH (p:Package)
            RETURN p
            """,
        )
        packages = []
        for record in result:
            packages.append(record)
        return packages

    return db.execute_read(get_packages_tx)


def db_package_delete_all():
    def delete_packages_tx(tx):
        return tx.run(
            """
            MATCH (p:Package)
            DETACH DELETE p
            """,
        )

    db.execute_write(delete_packages_tx)


def _db_merge_package_and_dependents(package: Package, fully_searched_packages: Set[str]):
    # ended up removing since we want to do relationships after all packages are created
    # create or update package in db if it does not already exist
    db_merge_package(package)
    fully_searched_packages.add(package.id)

    for d in package.dependencies:
        get_package(package.id)
        # db_merge_package_id_only(d.package)
        db_dependency_merge(package.id, d)


def db_merge_package_id_only(package_id: str):
    """Add package to db if it does not exist"""
    print(f"\t merge package {package_id} - id only")

    def merge_package_id_only(tx):
        result = tx.run(
            """
            MERGE (p:Package {
                package_id: $package_id
            })
            ON CREATE SET p.created = timestamp()
            ON MATCH SET
            p.counter = coalesce(p.counter, 0) + 1,
            p.accessTime = timestamp()
            """,
            package_id=package_id,
        )
        return result

    return db.execute_write(merge_package_id_only)


def db_merge_package(package: Package):
    print(f"\t merge package {package.id}")
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
    # print(f"searching for package in db: {package_name}")

    def match_package_tx(tx):
        result = tx.run(
            """
            MATCH (p:Package)
            WHERE p.package_id = $package_id
            RETURN p
            """,
            package_id=package_name,
        )
        return result.single()

    record = db.execute_read(match_package_tx)

    # print(f"record: {record}")

    if record is None:
        print("Package not found in db. None returned")
        return None

    node: Node = record["p"]
    # print(f"node: {node}")
    if node is None:
        print("Package found in db has no node. None returned. ")
        return None

    dependencies = get_dependencies_from_db(package_name)
    p = Package(
        id=node.get("package_id"),
        description=node.get("description"),
        latest_version=node.get("latest_version"),
        dependencies=dependencies,
    )
    return p


def _get_package_from_cache(
    package_name: str, fully_searched_packages: Set[str]
) -> Package | None:
    # print(f"searching for package in cache: {package_name}")
    # app.logger.info(f"getting {package_name}")
    cache.clean_if_invalid(package_name)
    # print("diagnose1")
    # diagnose(package_name)
    if cache.exists(package_name):
        app.logger.info(f"{package_name} is cached")
        r_dict = cache.load(package_name)
        p = Package.from_package_json(r_dict)
        _db_merge_package_and_dependents(p, fully_searched_packages)
        # db_merge_package(p)
        return p
    return None


# todo; send request to cache
def _scrape_package_from_online(package_name: str) -> bool:
    app.logger.info(f"{package_name} is not cached. Scraping from online")
    r_dict = scrape_package_json(package_name)

    if r_dict is not None:
        cache.save(package_name, r_dict)
        # p = Package.from_package_json(r_dict)
        # _db_merge_package_and_dependents(p)
        # db_merge_package(p)
        # return p
        return True
    # print("diagnose2")
    # diagnose(package_name)
    print(f"Failed to scrape {package_name}")
    return False


def get_package(
    package_name: str, fully_searched_packages: Set[str] = set()
) -> Package | None:
    # print(f"\n\nsearching for package: {package_name}")

    # db is now the single source of truth. update cache to update db. but only get
    # package data from db

    # todo. check that the package is up to date with the cache. write logic for this
    outerCount = 0
    p: Package | None = None
    while p is None:
        assert outerCount < 3

        p = _get_package_from_db(package_name)
        if p is not None:
            # print(f"package {package_name} found in the database")
            return p

        count = 0
        # print(f"package not in db. Checking cache {package_name}")
        # app.logger.info(f"getting {package_name}")
        cache.clean_if_invalid(package_name)
        # print("diagnose1")
        while not cache.exists(package_name):
            assert count < 4
            # diagnose(package_name)
            # if cache.exists(package_name):
            #     is_cached = True
            #     app.logger.info(f"{package_name} is cached")
            #     r_dict = cache.load(package_name)
            #     p = Package.from_package_json(r_dict)
            #     # db_merge_package(p)
            app.logger.info(f"{package_name} is not cached. Scraping from online")
            r_dict = scrape_package_json(package_name)

            if r_dict is not None:
                cache.save(package_name, r_dict)
            # else:
            # print("diagnose2")
            # diagnose(package_name)
            # print(f"Failed to scrape {package_name}")
            count += 1

        # print("cache file written. update db from cache")
        r_dict = cache.load(package_name)
        """Update the db package based on the information in the cache file. Do not return a
        Package since the DB is the one source of Truth. Since all Packages are now made from
        DB data, it is easy to know where problems arise.
        """
        id = r_dict.get("_id")
        description = r_dict.get("description")
        latest_version = r_dict.get("dist-tags", {}).get("latest")
        if not description:
            description = ""
        assert id is not None
        # some packages have no dependencies. represent this as an empty dict
        dependency_dict: Dict[str, str] = (
            r_dict.get("versions", {}).get(latest_version, {}).get("dependencies", {})
        )
        # print(f"dependency_dict = {dependency_dict} ---------------------------------")
        dependencies: list[Dependency] = []
        for package, version in dependency_dict.items():
            # print(f"\taaaaa: b{package}, {version}")
            dependencies.append(Dependency(package, version))
        # print(f"dependencies = {dependencies}")
        temp = Package(
            id,
            latest_version,
            dependencies,
            description,
        )
        db_merge_package(temp)
        fully_searched_packages.add(package_name)

        for d in dependencies:
            if d.package not in fully_searched_packages:
                get_package(d.package, fully_searched_packages)
                fully_searched_packages.add(d.package)
            db_dependency_merge(package_name, d)
        outerCount += 1


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
