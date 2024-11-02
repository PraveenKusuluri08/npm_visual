from npmvisual.commonpackages import get_popular_package_names
from npmvisual.data import bp
from npmvisual.data.db_package import (
    db_packages_delete_all,
    db_recursive_network_search_and_scrape,
    db_recursive_scrape_slow,
)


@bp.route("/network")
def network():
    db_recursive_network_search_and_scrape(["express"])
    # db_package_delete_all()
    return "success"


@bp.route("/scrapeAll", methods=["GET"])
def scrape_everything():
    to_search = get_popular_package_names()
    db_recursive_scrape_slow(to_search)
    return "success"


# @bp.route("/deletePackages")
def delete_packages():
    db_packages_delete_all()
    return "success"
