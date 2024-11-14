import json
import os
import random
from typing import Any

from flask import current_app as app
from neo4j.graph import Node
import npmvisual.utils as utils

from npmvisual import db

# from npmvisual._models.package import package_from_json
# from npmvisual._models.neomodel_connection_test import NeomodelConnectionTest
from npmvisual._models import package
from npmvisual._models.package_version import PackageVersion, package_version_from_json
from npmvisual._models.packageNode import PackageNode
from npmvisual._models.packument import Packument
from npmvisual.data import cache
from npmvisual.data.db_dependency import (
    db_merge_package_full,
)
from npmvisual.data.scraper import scrape_package_json
from npmvisual.models import Dependency, NeomodelConnectionTest, Package
from npmvisual.utils import Infinity, infinity, nsprint


def _get_package_from_db_node(node: Node, d_list: list[Dependency]):
    return Package(
        id=node.get("package_id"),
        description=node.get("description"),
        latest_version=node.get("latest_version"),
        dependencies=d_list,
        # dist_tags=Dist_Tags(latest="todo"),
    )


def db_recursive_scrape_slow(
    packages_to_search: list[str],
) -> bool:
    """
    to_search: list[str] = packages_to_search.copy()
    found: dict[str, float] = {}

    while len(to_search) > 0:
        print(f"\nsearching for {to_search}")
        newly_found = db_search(to_search)
        package: Package
        for package in newly_found:
            found[package.id] = time.time()
            to_search.remove(package.id)
            for d in package.dependencies:
                if d.package not in found:
                    # print(f"\tadding {d.package} to to_search")
                    to_search.append(d.package)
        print(f"len(newly_found)={len(newly_found)}")
        print(f"len(found)={len(found)}")
        if len(newly_found) == 0:
            for package_name in to_search:
                was_already_cached = _find_package_and_save_to_cache(package_name)
                print(f"was_already_cached = {was_already_cached}")
                r_dict = cache.load(package_name)
                temp = json_to_package(r_dict)
                db_merge_package_full(temp)
                if not was_already_cached:
                    print("sleeping for 3 seconds")
                    time.sleep(3)
                # print(f"saved package {y} to db")
    """
    return True


def gb_recursive_network_search_and_scrape(
    packages_to_search: list[str],
) -> dict[str, PackageNode]:
    to_search: list[str] = packages_to_search.copy()
    found: dict[str, PackageNode] = {}
    could_not_find: list[str] = []

    depth = 0
    while len(to_search) > 0 and depth <= 50:
        print(f"\nsearching for {to_search}")
        # newly_found = db_search(to_search)
        newly_found = PackageNode.nodes.filter(package_id__in=to_search)
        package: PackageNode
        for package in newly_found:
            # package.pretty_print()
            found[package.package_id] = package
            to_search.remove(package.package_id)
            if package.dependency_id_list:
                print(333)
                for d in package.dependency_id_list:
                    print(f"adding d 22222")
                    if d not in found:
                        print(f"adding d 33333")
                        # print(f"\tadding {d.package} to to_search")
                        to_search.append(d)
        print(f"len(newly_found)={len(newly_found)}")
        print(f"len(found)={len(found)}")
        count = 0
        if len(newly_found) == 0:
            for package_name in to_search:
                if count > 20:
                    break
                count += 1
                next_to_add = find_or_scrape(package_name)
                if next_to_add:
                    found[package_name] = next_to_add
                else:
                    could_not_find.append(package_name)

                # _find_package_and_save_to_cache(package_name)
                # r_dict = cache.load(package_name)

        depth += 1
    return found


def find_or_scrape(package_name: str) -> PackageNode | None:
    found = PackageNode.nodes.get(package_name=package_name)
    if found:
        return found
    print(f"searching internet for {package_name}")
    json_dict: dict[str, Any] | None = scrape_package_json(package_name)
    if json_dict is None:
        return None
    with open(f"output{1}.json", "w") as file:
        json.dump(json_dict, file, indent=4)

    print("7" * 100)
    new_packument = Packument.from_json(json_dict)
    print("8" * 100)
    print(new_packument)
    print("9" * 100)

    if new_packument is None:
        return None

    temp = PackageNode.from_packument(new_packument)
    print(f"saving {package_name} to db")
    temp.save()
    return temp
    # temp = Package.from_json(r_dict)
    # db_merge_package_full(temp)


def db_search(to_search: list[str]) -> list[Package]:
    # print(f"searching for {to_search}")
    found: list[Package] = []

    def _get_packages_tx(tx):
        # print(f"\nabout to search for {to_search}")
        result = tx.run(
            """
            MATCH (seed:Package)
            WHERE seed.package_id IN $to_search
            OPTIONAL MATCH (seed)-[rel:DependsOn]->(dependency:Package)
            WITH seed, rel, dependency
            RETURN seed, 
                COLLECT({
                    version: rel.version,
                    package_id: dependency.package_id
                })
                AS dependencies
            """,
            to_search=to_search,
        )

        # print(f"search result={result}")
        for record in result:
            p_data: Node = record["seed"]
            # print(f"processing package {p_data.get('package_id')}")
            d_list: list = record["dependencies"]
            # print(f"dependencies of record are {d_list}")
            dependencies = []
            for d in d_list:
                # print(type(d["version"]))
                if d["version"] is None and d["package_id"] is None:
                    continue
                dependencies.append(Dependency(d["package_id"], d["version"]))
            p = _get_package_from_db_node(p_data, dependencies)
            found.append(p)

    db.execute_read(_get_packages_tx)
    return found


def db_packages_get_all() -> list[Package]:
    def _get_packages_tx(tx):
        result = tx.run(
            """
            MATCH (p:Package)
            RETURN p
            """,
        )
        packages = []
        for record in result:
            packages.append(record)
        return packages

    return db.execute_read(_get_packages_tx)


def db_packages_delete_all():
    def delete_packages_tx(tx):
        return tx.run(
            """
            MATCH (p:Package)
            DETACH DELETE p
            """,
        )

    db.execute_write(delete_packages_tx)


def _find_package_and_save_to_cache(package_name: str) -> bool:
    cache.clean_if_invalid(package_name)
    for _ in range(4):
        if cache.exists(package_name):
            return True
        app.logger.info(f"{package_name} is not cached. Scraping from online")
        r_dict = scrape_package_json(package_name)

        if r_dict is not None:
            cache.save(package_name, r_dict)
    return False


def _get_num_of_packages_in_names_json() -> int:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path + "/package_cache/names.json")
    with open(file_path) as file:
        return sum(1 for line in file)


# def db_scrape_everything2():
#     jim = Person(name="Jim", age=3).save()
#     jim.age = 4
#     jim.save()  # Update, (with validation)


def db_scrape_everything():
    x = NeomodelConnectionTest(name="testing4")
    x.save()
    print(x)

    # item = NeomodelConnectionTest()
    #
    # from npmvisual import db
    #
    # db.save(item)
    # item.save()
    print("scrape everything called")

    # create_an_item()
    limit = 1
    # remove this in a bit
    n = _get_num_of_packages_in_names_json()
    offset = random.randint(0, n)
    sleep_time = 10  # seconds

    all_packages_not_yet_scraped: set = _get_all_package_names(limit, offset)
    failed_to_scrape = set()
    total_count = len(all_packages_not_yet_scraped)
    finished: dict[str, Packument] = {}
    this_batch: set[Packument] = set()

    count = 0
    while all_packages_not_yet_scraped and count < limit:
        next_package_name = all_packages_not_yet_scraped.pop()
        print(f"\nAdding {count}/{total_count} : {len(failed_to_scrape)} failed.")
        print(f"\tNext Package: {next_package_name}. ")
        count += 1
        json_dict: dict[str, Any] | None = None  # scrape_package_json(next_package_name)
        with open(f"output{count}.json") as file:
            json_dict = json.load(file)

        if json_dict is None:
            failed_to_scrape.add(next_package_name)

        else:
            # save a version for testing purposes
            # with open(f"output{count}.json", "w") as file:
            #     json.dump(json_dict, file, indent=4)
            # print(
            #     "\n Json data downloaded and saved. Creating packument -------------------------------------------------------"
            # )
            new_packument = Packument.from_json(json_dict)
            if new_packument is not None:
                # print(
                #     "\n packument created. Pretty Printing------------------------------------------------------\n"
                # )
                print(" My Pretty Print ###############################################")
                new_packument.pretty_print()
                print(" My Pretty Print End ###########################################")
                all = PackageNode.nodes.all()
                for p in all:
                    p.delete()
                p_node = PackageNode.from_packument(new_packument)
                p_node.save()

                # from npmvisual import db

                # db.save(p_node)
                print("success")

            #
            # all_versions: dict[str, Any] | None = json_dict.get("versions")
            # if all_versions:
            #     version_count = 0
            #     for version, value in all_versions.items():
            #         # print(f"version: {version}")
            #         # print(f"value: {value}")
            #         if version_count > 0:
            #             break
            #         next_package: PackageVersion | None = package_version_from_json(value)
            #         if next_package:
            #             db_merge_package_full(next_package)
            #             id: str = next_package.id
            #             finished[id] = next_package
            #         else:
            #             failed_to_scrape.add(next_package_name)
            #         version_count += 1
            #
            #         # print(f"\tadded package to db: {next_package}")

    print(f"\nScraped Everything{count}/{total_count} : {len(failed_to_scrape)} failed.")


def search_and_scrape_recursive(
    package_names: set[str],
    max_count: int | Infinity = infinity,
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
        print(f"search_and_scrape_recursive round {count} -------------------")
        nsprint(f"  db searching for: {to_search}")
        (in_db, not_in_db) = search_packages_recursive(to_search)
        found.update(in_db)
        to_search.difference(set(in_db.keys()))

        if len(not_in_db) == 0:
            break

        print(f"  Some packages not in db. Searching online: {not_in_db}")
        (scraped, not_scraped) = scrape_packages(not_in_db)
        print(
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
        print("---====================----")
        nsprint(f"searching db for: {to_search}", 1)
        print("-------------------")
        (newly_found, newly_not_found) = search_packages(to_search)
        not_found.update(newly_not_found)
        nsprint(f"found in db: {[newly_found.keys()]}", 1)
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


def scrape_package(package_name: str) -> PackageNode | None:
    json_dict = scrape_package_json(package_name)
    # versions: dict[str, Any] = json_dict.get("versions")  # type: ignore
    # if versions and len(versions) > 0:
    #     last_item: Any = sorted(versions.items())[-1][1]
    #     funding = last_item.get("bugs")
    #     print(f"bugs:{funding}")

    if not json_dict:
        return None
    packument = Packument.from_json(json_dict)
    if not packument:
        return None
    pn = PackageNode.from_packument(packument)
    if pn:
        pn.save()
    return pn
