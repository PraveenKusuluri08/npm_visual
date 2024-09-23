from typing import Dict, List

import requests

from npmvisual.commonpackages import get_popular_packages
from npmvisual.package import Package


def scrape_package(name: str) -> Package | None:
    # print(f"scraping package named {name}")
    url = f"https://registry.npmjs.org/{name}"
    # print(url)
    response = requests.get(url)
    if response.status_code == 200:
        r_dict = response.json()

        latest_version = r_dict.get("dist-tags", {}).get("latest")

        # some packages have no dependencies. represent this as an empty dict
        dependencies: Dict[str, str] = (
            r_dict.get("versions", {}).get(latest_version, {}).get("dependencies", {})
        )

        p = Package(
            r_dict.get("_id"), r_dict.get("description"), latest_version, dependencies
        )
        # print("scraped " + p.id.__str__())
        return p
    else:
        print(f"Failed to fetch data for {name}, status code: {response.status_code}")

    print("errrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrror")
    return None


def scrape_package_ego_network(to_search: List[str], max=100) -> Dict[str, Package]:
    data: Dict[str, Package] = {}
    # print(to_search)

    count = 1
    while count < max:
        count += 1
        if len(to_search) == 0:
            break
        # print("\n\n-------------------------------------------------")
        print("to_search = " + to_search.__str__())
        # print("\ndata = " + data.keys().__str__())
        next_id = to_search.pop()
        print("count = " + count.__str__() + "next = " + next_id)
        if next_id not in data:
            next_package = scrape_package(next_id)
            # print("next_package = " + next_package.__str__())
            if next_package is None:
                return {}
            data[next_id] = next_package
            for d in next_package.dependencies:
                if d not in data:
                    to_search.append(d)
    return data


def scrape_all_data_long():
    scrape_all_data(10)


def scrape_all_data(max=1000) -> Dict[str, Package]:
    print()
    to_search = get_popular_packages()
    return scrape_package_ego_network(to_search, max)
