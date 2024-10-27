from typing import Dict, List

import networkx as nx
from flask import Blueprint, jsonify

from npmvisual.commonpackages import get_popular_packages

from .data.package import Package, get_package

bp = Blueprint("utils", __name__)


@bp.route("/scrapeAll", methods=["GET"])
def scrape_all():
    scrape_all_data(1000)
    return "success"


@bp.route("/dependencies/<package_name>", methods=["GET"])
def get_package_dependencies(package_name):
    g = build_graph_ego_network(package_name)
    return jsonify(g)


@bp.route("/getPopularNetwork")
def get_popular_network():
    g = build_popular_network()
    return jsonify(g)


def build_graph(packages: Dict[str, Package]):
    G = nx.DiGraph()
    for p in packages.values():
        # print(p)
        G.add_node(p.id)

    for p in packages.values():
        for d in p.dependencies:
            G.add_edge(d.package, p.id)
    return G


def build_popular_network():
    to_search = get_popular_packages()
    return build_graph_network(to_search, 2000)


def build_graph_network(packages: List[str], max=1000):
    data: Dict[str, Package] = get_package_ego_network(packages, max)
    graph = build_graph(data)
    graph_data = nx.node_link_data(graph)
    return graph_data


def build_graph_ego_network(package_name: str):
    packages = [package_name]
    data: Dict[str, Package] = get_package_ego_network(packages, 1000)
    graph = build_graph(data)
    graph_data = nx.node_link_data(graph)
    return graph_data


# build_graph_from_seeds
def get_package_ego_network(to_search: List[str], max=100) -> Dict[str, Package]:
    # idea. maybe use a priority queue of some kind
    to_search.reverse()
    data: Dict[str, Package] = {}
    # print(to_search)

    count = 1
    while count < max:
        count += 1
        if len(to_search) == 0:
            break  # No remaining dependencies remaining. Success
        # print("\n\n-------------------------------------------------")
        # print("to_search = " + to_search.__str__())
        # print("\ndata = " + data.keys().__str__())
        next_id = to_search.pop()
        # print("count = " + count.__str__() + "next = " + next_id)
        if next_id not in data:
            next_package: Package | None = get_package(next_id)
            # print("next_package = " + next_package.__str__())
            if next_package is None:
                return {}
            data[next_id] = next_package
            for d in next_package.dependencies:
                if d.package not in data:
                    to_search.append(d.package)
    print(f"graph created with {count} packages")
    return data


def scrape_all_data(max=1000) -> Dict[str, Package]:
    to_search = get_popular_packages()
    return get_package_ego_network(to_search, max)
