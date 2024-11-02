from typing import Dict, List

import networkx as nx
from flask import Blueprint, jsonify

from npmvisual.commonpackages import get_popular_package_names
from npmvisual.data import get_packages

from .data.package import Package

bp = Blueprint("utils", __name__)


@bp.route("/dependencies/<package_name>", methods=["GET"])
def get_package_dependencies(package_name):
    packages = [package_name]
    data: Dict[str, Package] = get_packages(packages)
    return format_for_frontend(data)


@bp.route("/getPopularNetwork")
def get_popular_network():
    to_search = get_popular_package_names()
    data: Dict[str, Package] = get_packages(to_search)
    return format_for_frontend(data)


def format_as_nx(data: dict[str, Package]):
    G = nx.DiGraph()
    for p in data.values():
        G.add_node(p.id)

    for p in data.values():
        for d in p.dependencies:
            G.add_edge(d.package, p.id)
    graph_data = nx.node_link_data(G)
    return graph_data


def format_for_frontend(data):
    nx_graph = format_as_nx(data)
    return jsonify(nx_graph)
