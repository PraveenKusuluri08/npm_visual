from flask import current_app as app

from npmvisual.package import Package

from .cache import (
    exists,
    load,
    save,
    diagnose,
    clean_if_invalid,
)
from .scraper import scrape_package_json


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
