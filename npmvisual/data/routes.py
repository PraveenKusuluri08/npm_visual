from npmvisual._models.packageNode import PackageNode
from npmvisual.commonpackages import get_popular_package_names
from npmvisual.data import bp
from npmvisual.utils import get_all_package_names

from .db_package import (
    scrape_packages as db_scrape_packages,
)
from .db_package import (
    search_packages,
)

# @bp.route("/deletePackages")
# def delete_packages():
#     db_packages_delete_all()
#     return "success"

########################################################


@bp.route("/getDBPackages")
def get_packages(package_names: list[str]) -> dict[str, PackageNode]:
    (found, not_found) = search_packages(set(package_names))
    return found


@bp.route("/getDBPopularPackages")
def get_popular_packages() -> dict[str, PackageNode]:
    to_search = get_popular_package_names()
    return get_packages(list(to_search))


@bp.route("/getAllDBPackages")
def get_all_packages() -> dict[str, PackageNode]:
    to_search = get_all_package_names()
    return get_packages(list(to_search))


@bp.route("/getDBPackage")
def get_package(package_name: str) -> dict[str, PackageNode]:
    return get_packages(list(package_name))


########################################################
@bp.route("/scrapePackages")
def scrape_packages(package_names: list[str]) -> str:
    (found, not_found) = db_scrape_packages(set(package_names))
    return (
        f"Successfully scraped {len(found)} packages.\n"
        f"Failed to scrape {len(not_found)} packages."
    )


@bp.route("/scrapePopularPackages")
def scrape_popular_packages() -> str:
    to_search = get_popular_package_names()
    return scrape_packages(list(to_search))


@bp.route("/scrapeAllPackages")
def scrape_all_packages() -> str:
    to_search = get_all_package_names()
    return scrape_packages(list(to_search))


@bp.route("/scrapePackage/<package_name>")
def scrape_package(package_name: str) -> str:
    return scrape_packages(list(package_name))
