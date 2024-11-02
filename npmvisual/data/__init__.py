"""
This is the tool you should use to load packages. It will retrieve it from the db or from
the web if it is not already cached.

We have several data sources. db, cached package.json pages, and online scraping. This
tool decides where to retrieve data from.
"""

from flask import Blueprint

from npmvisual.models import Package

from .db_package import db_recursive_network_search_and_scrape

bp = Blueprint("data", __name__)

from npmvisual.data import cache, db, scraper


# @bp.route("/clearCache")
def clear_cache():
    clear_cache()
    return "success"


def get_package(
    package_name: str,
) -> dict[str, Package]:
    return get_packages([package_name])


def get_packages(
    packages_to_search: list[str],
) -> dict[str, Package]:
    return db_recursive_network_search_and_scrape(packages_to_search)
