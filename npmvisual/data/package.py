from npmvisual import db
from typing import Self
from dataclasses import dataclass
from typing import Dict

from flask import current_app as app

from npmvisual.data.scraper import scrape_package_json
from .cache import clean_if_invalid, exists, load, save


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

    def addToDB(self):
        print(db)
        # with db.driver() as session:
        # db.driver?.execute_write("")
        # toto
        # r = session.execute_write()


def get_package(package_name: str) -> Package | None:
    # app.logger.info(f"getting {package_name}")
    clean_if_invalid(package_name)
    # print("diagnose1")
    # diagnose(package_name)
    if exists(package_name):
        app.logger.info(f"{package_name} is cached")
        r_dict = load(package_name)

    else:
        app.logger.info(f"{package_name} is not cached. Scraping from online")
        r_dict = scrape_package_json(package_name)
        save(package_name, r_dict)
    if r_dict is not None:
        return Package(r_dict)
    else:
        # print("diagnose2")
        # diagnose(package_name)
        print(f"Failed to scrape {package_name}")
        return None


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
