from typing import Dict, List
import matplotlib.pyplot as plt
import networkx as nx
import requests

from .package import Package


def scrape_package(name: str) -> Package | None:
    print(f"scraping package named {name}")
    url = f"https://registry.npmjs.org/{name}"
    print(url)
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
        print("scraped " + p.id.__str__())
        return p
    print("errrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrror")
    return None


def create_graph():
    G = nx.MultiDiGraph()

    data = scrape_all_data()

    for package in data:
        main_package = package.id

        G.add_node(main_package, label=main_package)
        for dependency, _ in package.dependencies:
            G.add_node(dependency, label=dependency)
            G.add_edge(dependency, main_package)

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=False, node_size=500, node_color="lightblue")

    labels = nx.get_node_attributes(G, "label")
    nx.draw_networkx_labels(G, pos, labels, font_size=10)

    # nx.draw_networkx_nodes(
    #     G, pos, nodelist=[main_package], node_color="red", node_size=700
    # )

    plt.savefig("graph.png")


def scrape_all_data() -> List[Package]:
    seed = "express"
    data: Dict[str, Package] = {}
    s = scrape_package(seed)
    if s is None:
        return []
    data[s.id] = s
    to_search: List[str] = list(s.dependencies.keys())
    print()
    print(to_search)

    count = 1
    while count < 50:
        if len(to_search) == 0:
            break
        print("\n\n-------------------------------------------------")
        print("to_search = " + to_search.__str__())
        print("\ndata = " + data.keys().__str__())
        next_id = to_search.pop()
        print("next = " + next_id)
        if next_id not in data:
            next_package = scrape_package(next_id)
            print("next_package = " + next_package.__str__())
            if next_package is None:
                return []
            data[next_id] = next_package
            for d in next_package.dependencies:
                if d not in data:
                    to_search.append(d)
    return list(data.values())

    # count = 1
    # limit = 100
    #
    # for id in to_search_copy:
    #     name, package = to_search.pop(name)
    #
    #     p = scrape_data(name)
    #     data.append(p)
    #     count++
    #
    # for package_name in package_names:
    #     url = f"https://registry.npmjs.org/{package_name}"
    #     response = requests.get(url)
    #     if response.status_code == 200:
    #         r_dict = response.json()
    #
    #         latest_version = r_dict.get("dist-tags", {}).get("latest")
    #
    #         dependencies = (
    #             r_dict.get("versions", {})
    #             .get(latest_version, {})
    #             .get("dependencies", None)
    #         )
    #
    #         p = Package(
    #             r_dict.get("_id"), r_dict.get("description"), latest_version, dependencies
    #         )
    #         data.append(p)
    #     else:
    #         print(
    #             f"Failed to fetch data for {package_name}, status code: {response.status_code}"
    #         )
    #
    # return data


def fetch_dependencies(package_name, version="latest"):
    url = f"https://registry.npmjs.org/{package_name}/{version}"
    response = requests.get(url)
    package_data = response.json()

    dependencies = package_data.get("dependencies", {})
    return dependencies


def build_graph(package_name, version="latest"):
    G = nx.DiGraph()
    G.add_node(package_name)

    dependencies = fetch_dependencies(package_name, version)

    for dep, _ in dependencies.items():
        G.add_node(dep)
        G.add_edge(package_name, dep)

    return G


def build_big_graph(packages: List[Package]):
    G = nx.DiGraph()
    for p in packages:
        G.add_node(p.id)

    for p in packages:
        for e in p.dependencies:
            G.add_edge(e, p.id)
    return G
