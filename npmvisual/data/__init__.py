"""
This is the tool you should use to load packages. It will retrieve it from the db or from
the web if it is not already cached.

We have several data sources. db, cached package.json pages, and online scraping. This
tool decides where to retrieve data from.
"""

from .cache import clear_cache
from .main import get_package

__all__ = ["get_package", "clear_cache"]
