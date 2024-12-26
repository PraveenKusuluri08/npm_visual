"""
This is the tool you should use to load packages. It will retrieve it from the db or from
the web if it is not already cached.

We have several data sources. db, cached package.json pages, and online scraping. This
tool decides where to retrieve data from.
"""

from flask import Blueprint

bp = Blueprint("data", __name__)

from npmvisual.data import routes

from .main import (
    scrape_packages,
    search_and_scrape_recursive,
    db_search_packages,
    get_db_all,
    get_db_all_names,
)
