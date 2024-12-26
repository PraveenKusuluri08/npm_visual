from typing import Any
import logging

from neomodel.sync_.match import Collect
from neomodel import db

from npmvisual._models.dependency import Dependency
from npmvisual._models.package import PackageData
import npmvisual.utils as utils
from npmvisual.data.scraper import scrape_package_json
from npmvisual.models import Package, Packument


def get_db_all_names() -> list[str]:
    # todo: fix this once I learn how to use neomodel.

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
    to_search: set[str],
) -> dict[str, PackageData]:
    utils.nsprint(f"scrape_packages: scraping: {to_search}", 2)
    found: dict[str, PackageData] = {}
    for id in to_search:
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
    utils.nsprint("scrape_package()", 3)
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
        assert not any(bad_keys)
        utils.nsprint(f"Searching round {count}: db searching for: {to_search}", 1)
        (in_db, not_in_db) = search_db_recursive(to_search, found, max_count, count)
        found.update(in_db)
        to_search -= set(in_db.keys())

        # if len(not_in_db) == 0:
        #     utils.nsprint("nothing found, breaking from loop.")
        #     break

        if not_in_db:
            utils.nsprint(f"  Some packages not in db. Searching online: {not_in_db}")
            scraped: dict[str, PackageData] = scrape_packages(not_in_db)
            all_scraped.update(scraped)
            found.update(scraped)

            to_search = set()
            for package_data in scraped.values():
                for dependency in package_data.dependencies:
                    if dependency.package_id not in found:
                        to_search.add(dependency.package_id)

        # utils.nsprint(
        #     f"Scraping round {count} complete."
        #     f"Scrapped the following packages: {list(scraped.keys()), 1}"
        # )

        # if len(scraped) == 0:
        #     utils.nsprint("Could not scrape anything this round. Exiting loop")
        #     break
        count += 1
    # utils.nsprint(f"all_scraped: {all_scraped}")
    # utils.nsprint(f"found: {found}")
    # found.update(all_scraped)
    # print()
    # utils.nsprint(f"found: {found}")
    build_relationships(all_scraped)
    return found


def build_relationships(all_package_data: dict[str, PackageData]) -> None:
    """It is assumed that when this function is called, all the dependencies exist in
    the db for every single package. Make sure they exist before calling this function.
    Additionally, all the packages in all_package_data should already be saved in the db.
    """
    utils.nsprint(f"build_relationships({all_package_data})", 2)

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
    for package_data in all_package_data.values():
        if not package_data.dependencies:
            continue
        not_loaded = set(
            [dep.package_id for dep in package_data.dependencies]
        ).difference(all_package_data.keys(), cache.keys())
        # update cache
        if len(not_loaded):
            loaded = Package.nodes.filter(package_id__in=list(not_loaded))
            for p in loaded:
                cache[p.package_id] = p

        # build the relationships
        for dep in package_data.dependencies:
            dependency = _get_dependency(dep.package_id, all_package_data, cache)
            relationship = package_data.package.dependencies.connect(
                dependency, {"version": dep.version}
            )
            relationship.save()


def search_db_recursive(
    to_search: set[str],
    all_found: dict[str, PackageData],
    count_limit: int | utils.Infinity = utils.infinity,
    count=0,
) -> tuple[dict[str, PackageData], set[str]]:
    utils.nsprint(f"search_db_recursive(to_search: {to_search})", 2)
    to_search = to_search.copy()
    found: dict[str, PackageData] = {}
    not_in_db: set[str] = set()
    while len(to_search) > 0:
        newly_found: dict[str, PackageData] = db_search_packages(to_search)
        not_found = to_search - set(newly_found.keys())
        not_in_db.update(not_found)
        found.update(newly_found)
        to_search = set()
        for package_data in newly_found.values():
            for dependency in package_data.dependencies:
                id = dependency.package_id
                if id not in not_in_db and id not in found and id not in all_found:
                    # utils.nsprint(f"added dependency:{id}", 3)
                    to_search.add(id)
    return (found, not_in_db)


def db_search_packages(package_names: set[str]) -> dict[str, PackageData]:
    """
    Retrieves a list of packages and their dependencies.
    """
    utils.nsprint(f"db_search_packages({package_names})", 3)

    found: dict[str, PackageData] = {}
    packages = Package.nodes.filter(package_id__in=list(package_names))
    for package in packages:
        found[package.package_id] = PackageData(package, [])

    # Cypher query to fetch dependencies and their version
    query = """
    MATCH (p:Package)-[r:DEPENDS_ON]->(dep:Package)
    WHERE p.package_id IN $package_names
    RETURN p.package_id as package_id, 
        COLLECT({
            dep_package_id: dep.package_id, 
            dep_version: r.version
        }) as dependencies
    """
    results: list[tuple[str, list[dict[str, str]]]]
    results, meta = db.cypher_query(query, {"package_names": list(package_names)})  # type: ignore
    # print(meta)
    for result in results:
        package_id: str = result[0]
        db_dependencies: dict[str, str] = result[1]  # type: ignore
        # utils.nsprint(f"package_id: {str(package_id)}", 4)
        dep_list: list[Dependency] = []
        for row in db_dependencies:
            # utils.nsprint(f"row: {str(row)}", 4)
            dep_list.append(Dependency(row["dep_package_id"], row["dep_version"]))  # type: ignore
        found[package_id].dependencies = dep_list
    return found
