from typing import Any

import npmvisual.utils as utils
from npmvisual._models.package import PackageData
from npmvisual.models import Package

from . import database, scraper


def search_and_scrape_recursive(
    package_names: set[str],
    max_count: int | None,
) -> dict[str, PackageData]:
    # todo, consider adding depth limit by tracking the depth each package is away from
    # seeds
    print(f"\nstart of search_and_scrape_recursive: package_names:{package_names}")
    to_search: set[str] = package_names.copy()
    found: dict[str, PackageData] = {}
    all_scraped: dict[str, PackageData] = {}

    count = 0
    print(f"\nstart of search_and_scrape_recursive: to_search:{to_search}")
    while len(to_search) != 0:
        if max_count and len(found) < max_count:
            break
        bad_keys = [key for key in to_search if key in found]
        assert not any(bad_keys)
        utils.nsprint(f"Searching round {count}: db searching for: {to_search}", 1)
        (in_db, not_in_db) = database.search_db_recursive(
            to_search, found, max_count, count
        )
        found.update(in_db)
        to_search -= set(in_db.keys())
        if not_in_db:
            utils.nsprint(f"  Some packages not in db. Searching online: {not_in_db}")
            scraped: dict[str, PackageData] = scraper.scrape_packages(not_in_db)
            all_scraped.update(scraped)
            found.update(scraped)

            to_search = set()
            for package_data in scraped.values():
                for dependency in package_data.dependencies:
                    if dependency.package_id not in found:
                        to_search.add(dependency.package_id)
        count += 1
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
            relationship = package_data.package.dependencies.connect(  # pyright: ignore
                dependency, {"version": dep.version}
            )
            relationship.save()


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
