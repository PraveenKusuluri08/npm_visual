import networkx as nx
from flask import Blueprint, jsonify

from npmvisual._models.packageNode import PackageNode
from npmvisual.commonpackages import get_popular_package_names
from npmvisual.data import (
    search_and_scrape_recursive,
)
from npmvisual.utils import get_all_package_names

bp = Blueprint("network", __name__)


@bp.route("/getNetworks")
def get_networks(package_names: list[str]):  # todo add type
    (found, not_found) = search_and_scrape_recursive(set(package_names))
    if not_found:
        print(
            f"Successfully created network of size {len(found)}.\n"
            f"Failed to scrape or find: {not_found}"
        )
    return format_for_frontend(found)


@bp.route("/getPopularNetworks")
def get_popular_networks():
    to_search = get_popular_package_names()
    return get_networks(list(to_search))


@bp.route("/getAllNetworks")
def get_all_networks():
    to_search = get_all_package_names()
    return get_networks(list(to_search))


@bp.route("/getNetwork")
def get_network(package_name: str):
    return get_networks(list(package_name))


def format_as_nx(data: dict[str, PackageNode]):
    G = nx.DiGraph()
    for p in data.values():
        G.add_node(p.id)

    for p in data.values():
        if p.dependency_id_list:
            for d in p.dependency_id_list:
                G.add_edge(d, p.id)
    graph_data = nx.node_link_data(G)
    return graph_data


def format_for_frontend(data):
    nx_graph = format_as_nx(data)
    return jsonify(nx_graph)
