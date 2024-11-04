from npmvisual.commonpackages import get_popular_package_names
import os
import requests
import json
from npmvisual.data import bp
from npmvisual.data.db_package import (
    db_packages_delete_all,
    db_recursive_network_scrape_everything,
    db_recursive_network_search_and_scrape,
    db_recursive_scrape_slow,
)
from npmvisual.data.scraper import scrape_package_json


@bp.route("/network")
def network():
    db_recursive_network_search_and_scrape(["express"])
    # db_package_delete_all()
    return "success"


@bp.route("/scrapePopular", methods=["GET"])
def scrape_everything():
    to_search = get_popular_package_names()
    db_recursive_scrape_slow(to_search)
    return "success"


# @bp.route("/deletePackages")
def delete_packages():
    db_packages_delete_all()
    return "success"


@bp.route("/scrapeAll")
def fetch_all_packages():
    # search_and_save_everything()
    db_recursive_network_scrape_everything()
    return "dkjkd"
    # start = 0
    # size = 2500  # Adjust the size based on what the API allows
    #
    # for i in range(20):
    #     url = f"https://registry.npmjs.org/-/v1/search?size={size}&from={start}"
    #     response = requests.get(url)
    #     data = response.json()
    #     print(data["objects"])
    #
    #     # If no more packages are returned, break the loop
    #     if not data.get("objects"):
    #         print("no more objects")
    #         break
    #
    #     # Collect package data
    #     all_packages.extend(pkg["package"] for pkg in data["objects"])
    #     start += size  # Move to the next batch
    #
    # return all_packages
