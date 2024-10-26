from dataclasses import dataclass
from typing import Any, Dict

from flask import current_app as app
from neo4j._sync.work.transaction import ManagedTransaction

from npmvisual import db
from npmvisual.data.scraper import scrape_package_json

from npmvisual.data import cache


@dataclass
class Package:
    id: str
    description: str
    latest_version: str
    dependencies: Dict[str, str]

    def __init__(self, r_dict):
        self.id = r_dict.get("_id")
        self.description = r_dict.get("description")
        self.latest_version = r_dict.get("dist-tags", {}).get("latest")

        # some packages have no dependencies. represent this as an empty dict
        self.dependencies: Dict[str, str] = (
            r_dict.get("versions", {})
            .get(self.latest_version, {})
            .get("dependencies", {})
        )


def db_merge_package(package: Package):
    """Add package to db if it does not exist, update otherwise"""

    def merge_package_tx(
        tx: ManagedTransaction,
        package: Package,
    ):
        tx.run(
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

    db.execute_write(merge_package_tx, package)


def _get_package_from_db(package_name: str) -> Package | None:
    def match_package_tx(
        tx: ManagedTransaction,
        package_id: str,
    ):
        tx.run(
            """
            MERGE (p:Package)
            WHERE p.package_id = $package_id
            return p as package
            """,
            package_id=package_id,
        )

    return None


def _get_package_from_cache(package_name: str) -> Package | None:
    # app.logger.info(f"getting {package_name}")
    cache.clean_if_invalid(package_name)
    # print("diagnose1")
    # diagnose(package_name)
    if cache.exists(package_name):
        app.logger.info(f"{package_name} is cached")
        r_dict = cache.load(package_name)
        return Package(r_dict)
    return None


def _get_package_from_online(package_name: str) -> Package | None:
    app.logger.info(f"{package_name} is not cached. Scraping from online")
    r_dict = scrape_package_json(package_name)

    if r_dict is not None:
        cache.save(package_name, r_dict)
        return Package(r_dict)
    # print("diagnose2")
    # diagnose(package_name)
    print(f"Failed to scrape {package_name}")


def get_package(package_name: str) -> Package | None:
    p = _get_package_from_db(package_name)
    if p is not None:
        return p

    p = _get_package_from_cache(package_name)

    if p is not None:
        db_merge_package(p)
        return p

    return _get_package_from_online(package_name)


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
