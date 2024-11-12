import json
import pprint
import os
import random
import time
from typing import Any, Dict, Set

from flask import current_app as app
from neo4j.graph import Node

from npmvisual import db

# from npmvisual._models.package import package_from_json
# from npmvisual._models.neomodel_connection_test import NeomodelConnectionTest
from npmvisual._models.packageNode import PackageNode
from npmvisual._models.package_version import PackageVersion, package_version_from_json
from npmvisual._models.packument import Packument
from npmvisual.data import cache
from npmvisual.data.db_dependency import (
    db_merge_package_full,
)
from npmvisual.data.scraper import scrape_package_json
from npmvisual.models import Dependency, NeomodelConnectionTest, Package


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


def db_recursive_network_search_and_scrape(
    packages_to_search: list[str],
) -> dict[str, Package]:
    to_search: list[str] = packages_to_search.copy()
    found: dict[str, Package] = {}

    """
    depth = 0
    while len(to_search) > 0 and depth <= 50:
        print(f"\nsearching for {to_search}")
        newly_found = db_search(to_search)
        package: Package
        for package in newly_found:
            found[package.id] = package
            to_search.remove(package.id)
            for d in package.dependencies:
                if d.package not in found:
                    # print(f"\tadding {d.package} to to_search")
                    to_search.append(d.package)
        print(f"len(newly_found)={len(newly_found)}")
        print(f"len(found)={len(found)}")
        if len(newly_found) == 0:
            for package_name in to_search:
                _find_package_and_save_to_cache(package_name)
                r_dict = cache.load(package_name)
                temp = Package.from_json(r_dict)
                db_merge_package_full(temp)
        depth += 1
    """
    return found


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


def _get_all_package_names(max: int = 300, offset: int = 0) -> set:
    names = set()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path + "/package_cache/names.json")
    min = max
    max = offset + max
    with open(file_path) as file:
        data = json.load(file)
        i: int = 0
        for package_name in data:
            i += 1
            if i < min:
                continue
            names.add(package_name)
            if i >= max:
                break
    print(
        f"created a set of all package names with {len(names)} elements."
        f"This is {i-len(names)} less than the original file"
    )
    return names


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
                # print(" My Pretty Print ###############################################")
                # new_packument.pretty_print()
                # print(" My Pretty Print End ###########################################")
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
