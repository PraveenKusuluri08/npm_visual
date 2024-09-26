from flask import current_app as app

from npmvisual.package import Package

from .cache import exists, load, save
from .scraper import scrape_package_json


def get_package(package_name: str) -> Package | None:
    if exists(package_name):
        app.logger.info(f"{package_name} is cached")
        r_dict = load(package_name)
    else:
        r_dict = scrape_package_json(package_name)
        save(package_name, r_dict)
    if r_dict is not None:
        return Package(r_dict)
    else:
        print(f"Failed to scrape {package_name}")
        return None


def validate(r_dict):
    pass


def update_all():
    pass
