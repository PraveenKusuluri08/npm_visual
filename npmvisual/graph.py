from typing import Dict, List

import networkx as nx
from flask import Blueprint, jsonify

from npmvisual.commonpackages import get_popular_packages
from npmvisual.data.db_package import db_recursive_network_search_and_scrape

from .data.package import Package

bp = Blueprint("utils", __name__)


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
    return build_graph_network(to_search)


def build_graph_network(packages: List[str]):
    data: Dict[str, Package] = db_recursive_network_search_and_scrape(packages)
    return format_for_frontend(data)


def build_graph_ego_network(package_name: str):
    packages = [package_name]
    data: Dict[str, Package] = db_recursive_network_search_and_scrape(packages)
    return format_for_frontend(data)


def format_for_frontend(data: dict[str, Package]):
    graph = build_graph(data)
    graph_data = nx.node_link_data(graph)
    return graph_data
