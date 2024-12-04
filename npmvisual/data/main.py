from typing import Any

from npmvisual.data.scraper import scrape_package_json
from npmvisual.data.type_analyzer import NSType, NSTypeDB
from npmvisual.models import PackageNode, Packument
import npmvisual.utils as utils


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
    # NSTypeDB.print()
    return (found, not_found)


def scrape_package(package_name: str) -> PackageNode | None:
    json_dict = scrape_package_json(package_name)
    # NSType(json_dict)
    # raise Exception("stopping program for testing purposes")
    if not json_dict:
        return None

    # _print_json_variable(json_dict)
    packument = Packument.from_json(json_dict)
    if not packument:
        return None
    pn = PackageNode.from_packument(packument)
    if pn:
        pn.save()
    return pn


def create_dependency_relationship(
    package_node: PackageNode, cache: dict[str, PackageNode]
):
    cache_keys = set(cache)
    in_cache = [d for d in package_node.dependency_id_list if d in cache_keys]
    not_in_cache = [d for d in package_node.dependency_id_list if d not in cache_keys]

    (found, not_found) = search_packages(not_in_cache)


"""
help me write this python function. I am learning list comprehension and the best ways to use python lists and dicts. 


def create_dependency_relationship(
    package_node: PackageNode, cache: dict[str, PackageNode]
):
    all = package_node.dependency_id_list
    not_in_cache = [d for d in package_node.dependency_id_list if d not in cache]   
    in_cache = ???


i need to turn the list of all dependencies into two smaller lists
1)  a list of dependencies in the cache
2)  a list of dependencies not in the cache
              """


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

    print(f"\nstart of search_and_scrape_recursive: to_search:{to_search}")
    count = 0
    while len(to_search) != 0 and count < max_count:
        utils.nsprint(f"  db searching for: {to_search}")
        (in_db, not_in_db) = search_packages_recursive(to_search)
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
            if count >= count_limit:
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
    assert len(duplicates) == 0
    for packageNode in newly_found:
        # print(f"   -search_packages(): {packageNode.package_id}")
        # print(f"   xsearch_packages(): {packageNode.__str__()}")
        # print(f"   +search_packages(): {packageNode.pretty_print(3,3,10)}")
        assert packageNode and packageNode.package_id
        found[packageNode.package_id] = packageNode
        to_search.remove(packageNode.package_id)

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
