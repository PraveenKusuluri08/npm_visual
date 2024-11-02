from typing import Dict, List

import networkx as nx
from flask import Blueprint, jsonify

from npmvisual.commonpackages import get_popular_packages
from npmvisual.data.db_package import db_recursive_network_search_and_scrape
# from npmvisual.data.db_package import get_package

from .data.package import Package

bp = Blueprint("utils", __name__)


# @bp.route("/scrapeAll", methods=["GET"])
# def scrape_all():
#     scrape_all_data(1000)
#     return "success"


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
    data: Dict[str, Package] = db_recursive_network_search_and_scrape(packages)
    graph = build_graph(data)
    graph_data = nx.node_link_data(graph)
    return graph_data


def build_graph_ego_network(package_name: str):
    packages = [package_name]
    data: Dict[str, Package] = db_recursive_network_search_and_scrape(packages)
    graph = build_graph(data)
    graph_data = nx.node_link_data(graph)
    return graph_data
