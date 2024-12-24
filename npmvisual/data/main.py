from typing import Any
import logging

from neomodel.sync_.match import Collect

from npmvisual._models.package import PackageData
import npmvisual.utils as utils
from npmvisual.data.scraper import scrape_package_json
from npmvisual.models import Package, Packument


def get_db_all_names() -> list[str]:
    # todo: fix this once I learn how to use neomodel.
    from neomodel import db

    found = {}
    query = "MATCH (p:Package) RETURN p.package_id"

    # Execute the query using db.cypher_query
    results, _ = db.cypher_query(query)
    return results
    # query = "MATCH (p:PackageNode) RETURN p.package_name"
    # results, summary, keys = driver.execute_query(query, database_="neo4j")
    # newly_found = PackageNode.nodes.values("package_name")
    # print(results)
    # return newly_found


def get_db_all() -> dict[str, Package]:
    found: dict[str, Package] = {}
    newly_found = Package.nodes.all()
    for package in newly_found:
        found[package.package_id] = package
    return found


def save_packages(packages: set[Package]):
    for p in packages:
        p.save()


def scrape_packages(
    package_names: set[str],
) -> dict[str, PackageData]:
    print(f"    scrape_packages: scraping: {package_names}")
    found: dict[str, PackageData] = {}
    for id in package_names:
        scraped: PackageData | None = scrape_package(id)
        if not scraped:
            utils.nsprint(f"could not scrape: {id}", 3)
            # todo: try to scrape again if it fails
            scraped = Package.create_placeholder(id)
            scraped.package.save()
        found[id] = scraped
    utils.nsprint(f"scrape_packages: found: {found.keys()}", 2)
    return found


def _print_json_var(json_dict):
    some_key = json_dict.get("license")
    print(some_key)
    versions: dict[str, Any] = json_dict.get("versions")  # type: ignore
    vers_tag = None  # "3.0.0"
    # print(versions[vers_tag])
    if versions and vers_tag and versions[vers_tag]:
        # if versions and len(versions) > 0:
        last_item = versions[vers_tag]  # Any = sorted(versions.items())[-1][1]
        some_key = last_item.get("contributors")
        # structure = _get_type_structure(some_key)
        # _pretty_print_type_structure(structure)
        # nsprint(
        #     f"some_key:{some_key}",
        # )
    else:
        print("wtf??????????????????////")
    print(f"\nkey: {some_key}\n")


def scrape_package(package_name: str) -> PackageData | None:
    # try:
    json_dict = scrape_package_json(package_name)
    if not json_dict:
        logging.error(f"Failed to scrape package JSON for package: {package_name}")
        return None
    # _print_json_var(json_dict)
    packument = Packument.from_json(json_dict)
    if not packument:
        logging.error(
            f"Failed to convert scraped JSON to Packument for package: {package_name}"
        )
        return None
    packageData: PackageData = Package.from_packument(packument)
    if not packageData.package:
        logging.error(
            f"Failed to create Package object from Packument for package: {package_name}"
        )
        return None
    packageData.package.save()
    return packageData


def _pretty_print_type_structure(data: Any, indent: int = 0):
    # Helper function to format and print the data recursively
    space = " " * indent
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{space}{key}:")
            _pretty_print_type_structure(value, indent + 2)

    elif isinstance(data, list):
        for index, item in enumerate(data):
            print(f"{space}- Item {index + 1}:")
            _pretty_print_type_structure(item, indent + 2)

    else:
        # Print the type for primitive values
        print(f"{space}- Type: {data}")


def _get_type_structure(data: dict[str, Any]):
    def recursive_type_structure(value: Any) -> Any:
        if isinstance(value, dict):
            # Recurse into a dictionary and apply recursively to each key-value pair
            return {k: recursive_type_structure(v) for k, v in value.items()}

        elif isinstance(value, list):
            # Process each element in the list and return a list of types
            return [recursive_type_structure(v) for v in value]

        else:
            # Return the type of the value if it's a primitive or object type
            return [type(value).__name__]

    if data and data.items():
        return {k: recursive_type_structure(v) for k, v in data.items()}
    else:
        print(f"???????????????????????{data}")


def search_and_scrape_recursive(
    package_names: set[str],
    max_count: int | utils.Infinity = utils.infinity,
) -> dict[str, PackageData]:
    # todo, consider adding depth limit by tracking the depth each package is away from
    # seeds
    print(f"\nstart of search_and_scrape_recursive: package_names:{package_names}")
    to_search: set[str] = package_names.copy()
    found: dict[str, PackageData] = {}
    all_scraped: dict[str, PackageData] = {}

    count = 0
    print(f"\nstart of search_and_scrape_recursive: to_search:{to_search}")
    while len(to_search) != 0 and len(found) < max_count:
        bad_keys = [key for key in to_search if key in found]
        print(f"\nBad Keys: {bad_keys}")
        assert not any(bad_keys)
        utils.nsprint(f"Searching round {count}: db searching for: {to_search}")
        (in_db, not_in_db) = search_packages_recursive(
            to_search, all_scraped, max_count, count
        )
        found.update(in_db)
        to_search -= set(in_db.keys())

        if len(not_in_db) == 0:
            utils.nsprint("nothing found, breaking from loop.")
            break

        utils.nsprint(f"  Some packages not in db. Searching online: {not_in_db}")
        scraped: dict[str, PackageData]
        scraped = scrape_packages(not_in_db)
        all_scraped.update(scraped)

        utils.nsprint(
            f"Scraping round {count} complete."
            f"Scrapped the following packages: {list(scraped.keys())}"
        )
        # do not use info scraped directly from internet. get it from db next iteration
        to_search.update(scraped.keys())

        if len(scraped) == 0:
            utils.nsprint("Could not scrape anything this round. Exiting loop")
            break
        count += 1
    utils.nsprint(f"all_scraped: {all_scraped}")
    build_relationships(all_scraped)
    return found


def build_relationships(all_package_data: dict[str, PackageData]) -> None:
    """It is assumed that when this function is called, all the dependencies exist in
    the db for every single package. Make sure they exist before calling this function.
    Additionally, all the packages in all_package_data should already be saved in the db.
    """

    def _get_dependency(
        name: str, all_package_data: dict[str, PackageData], cache: dict[str, Package]
    ) -> Package:
        print(
            f" build_relationships(): name: {name}, all_package_data.keys(): {all_package_data.keys()}, cache: {cache}"
        )
        if name in all_package_data:
            return all_package_data[name].package
        else:
            return cache[name]

    cache: dict[str, Package] = {}
    # new_packages = Package.nodes.filter(package_id__in=list(all_package_data.keys()))
    # assert len(new_packages) == len(all_package_data)
    for package_data in all_package_data.values():
        if not package_data.dependencies:
            continue
        not_loaded = set(package_data.dependencies.keys()).difference(
            all_package_data.keys(), cache.keys()
        )
        # update cache
        if len(not_loaded):
            loaded = Package.nodes.filter(package_id__in=list(not_loaded))
            for p in loaded:
                cache[p.package_id] = p

        # build the relationships
        print()
        print(type(package_data.dependencies))
        print(package_data.dependencies)
        for name, version in package_data.dependencies.items():
            print(f"   name: {name}, version: {version}")
            dependency = _get_dependency(name, all_package_data, cache)
            relationship = package_data.package.dependencies.connect(
                dependency, {"version": version}
            )
            relationship.save()


def search_packages_recursive(
    to_search: set[str],
    all_scraped: dict[str, PackageData],
    count_limit: int | utils.Infinity = utils.infinity,
    count=0,
) -> tuple[dict[str, PackageData], set[str]]:
    to_search = to_search.copy()
    found: dict[str, PackageData] = {}
    not_found: set[str] = set()

    while len(to_search) > 0:
        utils.nsprint(f"Searching db for: {to_search}", 1)
        (newly_found, newly_not_found) = search_packages(to_search)
        not_found.update(newly_not_found)
        # utils.nsprint(f"newly_found: {newly_found}", 1)
        utils.nsprint(
            f"DB Search: Found: {len(newly_found)}, Not Found: {newly_not_found}, Found: {list(newly_found.keys())}",
            1,
        )
        to_search = set()
        for name, package in newly_found.items():
            package_data: PackageData = PackageData(package, package.get_dependencies())
            found[name] = package_data
            print(package_data)
            for dependency in package_data.dependencies:
                print(f"____ {dependency}")
                id = dependency.package_id
                if id not in not_found and id not in found:
                    utils.nsprint(f"added dependency:{id}", 3)
                    to_search.add(id)
    # utils.nsprint(
    #     f"recursive search round finished. found:{found}, not_fount: {not_found}", 1
    # )
    return (found, not_found)


def search_packages(package_names: set[str]) -> tuple[dict[str, Package], set[str]]:
    to_search: set[str] = package_names.copy()
    found: dict[str, Package] = {}

    newly_found = Package.nodes.filter(package_id__in=list(package_names))
    # ids = []
    # for package in newly_found:
    #     ids.append(package.package_id)
    #
    # duplicates = utils.find_duplicates(ids)
    # print("33" * 88)
    # print(duplicates)
    # assert len(duplicates) == 0
    for package in newly_found:
        found[package.package_id] = package
        if package.package_id in to_search:
            to_search.remove(package.package_id)
            # todo: fix this later, this should never happen, but it did when
            # creating a new neo4j db.

    return (found, to_search)


# def search_and_scrape(package_names: set[str]) -> tuple[dict[str, PackageNode], set[str]]:
#     to_search: set[str] = package_names.copy()
#     found: dict[str, PackageNode] = {}
#     not_found: set[str] = set()
#
#     newly_found = PackageNode.nodes.filter(package_id__in=package_names)
#     for name, packageNode in newly_found.items():
#         found[name] = packageNode
#         to_search.remove(name)
#
#     # Ensure 'scraped' is properly typed
#     scraped: dict[str, PackageNode]
#     could_not_scrape: set[str]
#     (scraped, could_not_scrape) = scrape_packages(to_search)
#
#     # Iterate over the dictionary correctly
#     for name, packageNode in scraped.items():
#         found[name] = packageNode
#         to_search.remove(name)
#     for name in could_not_scrape:
#         not_found.add(name)
#         to_search.remove(name)
#
#     assert len(to_search) == 0
#     return (found, not_found)
#
