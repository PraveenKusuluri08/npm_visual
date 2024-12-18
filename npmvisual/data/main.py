from typing import Any

from npmvisual.data.scraper import scrape_package_json
from npmvisual.models import PackageNode, Packument
import npmvisual.utils as utils


def get_db_all_names() -> list[str]:
    # todo: fix this once I learn how to use neomodel.
    from neomodel import db

    found = {}
    query = "MATCH (p:PackageNode) RETURN p.package_id"

    # Execute the query using db.cypher_query
    results, _ = db.cypher_query(query)
    return results
    # query = "MATCH (p:PackageNode) RETURN p.package_name"
    # results, summary, keys = driver.execute_query(query, database_="neo4j")
    # newly_found = PackageNode.nodes.values("package_name")
    # print(results)
    # return newly_found


def get_db_all() -> dict[str, PackageNode]:
    found: dict[str, PackageNode] = {}
    newly_found = PackageNode.nodes.all()
    for packageNode in newly_found:
        found[packageNode.package_id] = packageNode
    return found


def save_packages(packages: set[PackageNode]):
    for p in packages:
        p.save()


def scrape_packages(package_names: set[str]) -> tuple[dict[str, PackageNode], set[str]]:
    print(f"    scrape_packages: scraping: {package_names}")
    found: dict[str, PackageNode] = {}
    not_found: set[str] = set()
    for p in package_names:
        pn = scrape_package(p)
        if pn:
            found[p] = pn
        else:
            not_found.add(p)
    # print(f"    scrape_packages: found: {found.keys()}")
    return (found, not_found)


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


def scrape_package(package_name: str) -> PackageNode | None:
    json_dict = scrape_package_json(package_name)

    if not json_dict:
        return None

    # _print_json_var(json_dict)
    packument = Packument.from_json(json_dict)
    if not packument:
        return None
    pn = PackageNode.from_packument(packument)
    if pn:
        try:
            pn.save()
        except Exception as e:
            print("ser")
    return pn


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
) -> tuple[dict[str, PackageNode], set[str]]:
    # todo, consider adding depth limit by tracking the depth each package is away from
    # seeds
    print(f"\nstart of search_and_scrape_recursive: package_names:{package_names}")
    to_search: set[str] = package_names.copy()
    found: dict[str, PackageNode] = {}
    not_found: set[str] = set()

    count = 0
    print(f"\nstart of search_and_scrape_recursive: to_search:{to_search}")
    while len(to_search) != 0 and len(found) < max_count:

        utils.nsprint(f"  db searching for: {to_search}")
        (in_db, not_in_db) = search_packages_recursive(to_search, max_count)
        found.update(in_db)
        to_search.difference(set(in_db.keys()))

        if len(not_in_db) == 0:
            break

        utils.nsprint(f"  Some packages not in db. Searching online: {not_in_db}")
        (scraped, not_scraped) = scrape_packages(not_in_db)
        utils.nsprint(
            f"  Scraping round {count} complete."
            f"  Scrapped the following packages: {scraped.keys()}"
        )
        # do not use info scraped directly from internet. get it from db next iteration
        to_search.update(scraped.keys())
        not_found.update(not_scraped)

        if len(scraped) == 0:
            break
        count += 1

    return (found, not_found)


def search_packages_recursive(
    to_search: set[str],
    count_limit=utils.infinity,
    count=0,
) -> tuple[dict[str, PackageNode], set[str]]:
    to_search = to_search.copy()
    found: dict[str, PackageNode] = {}
    not_found: set[str] = set()

    while len(to_search) > 0:
        print()
        utils.nsprint(f"searching db for: {to_search}", 1)
        (newly_found, newly_not_found) = search_packages(to_search)
        not_found.update(newly_not_found)
        utils.nsprint(f"found in db: {[newly_found.keys()]}", 1)
        for name, packageNode in newly_found.items():
            found[name] = packageNode
            # print(f"  package {name} was already found. Will not search for it again")
            count += 1
            if count >= count_limit:  # todo this is temporary
                return (found, not_found)

        to_search = set()
        print("    Adding dependencies...")
        for p in newly_found.values():
            for dependency in p.dependency_id_list:
                if dependency not in not_found and dependency not in found:
                    to_search.add(dependency)
    return (found, not_found)


def search_packages(package_names: set[str]) -> tuple[dict[str, PackageNode], set[str]]:
    to_search: set[str] = package_names.copy()
    found: dict[str, PackageNode] = {}

    newly_found = PackageNode.nodes.filter(package_id__in=list(package_names))
    ids = []
    for packageNode in newly_found:
        ids.append(packageNode.package_id)

    duplicates = utils.find_duplicates(ids)
    # print("33" * 88)
    # print(duplicates)
    # assert len(duplicates) == 0
    for packageNode in newly_found:
        # print(f"   -search_packages(): {packageNode.package_id}")
        # print(f"   xsearch_packages(): {packageNode.__str__()}")
        # print(f"   +search_packages(): {packageNode.pretty_print(3,3,10)}")
        assert packageNode and packageNode.package_id
        found[packageNode.package_id] = packageNode
        # print(f"packageNode={packageNode} 00000000000000000000000000000000000")
        if packageNode.package_id in to_search:
            to_search.remove(packageNode.package_id)
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
