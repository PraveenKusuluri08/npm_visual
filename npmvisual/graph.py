import networkx as nx
from flask import Blueprint, jsonify, request

from npmvisual._models.packageNode import PackageNode
from npmvisual.commonpackages import get_popular_package_names
from npmvisual.data import (
    search_and_scrape_recursive,
)
from npmvisual.utils import get_all_package_names

bp = Blueprint("network", __name__)


@bp.route("/getNetworks/<package_names>", methods=["GET"])
def get_networks(package_names: list[str]):  # todo add type
    package_names = request.args.get("package_names", "").split(",")
    if not package_names:
        return jsonify({"error": "No package names provided"}), 400

    return _get_networks(package_names)


def _get_networks(package_names: list[str]):  # todo add type
    (found, not_found) = search_and_scrape_recursive(set(package_names))
    if not_found:
        print(
            f"Successfully created network of size {len(found)}.\n"
            f"Failed to scrape or find: {not_found}"
        )
    return format_for_frontend(found)


@bp.route("/getPopularNetworks", methods=["GET"])
def get_popular_networks():
    to_search = get_popular_package_names()
    return _get_networks(list(to_search))


@bp.route("/getAllNetworks", methods=["GET"])
def get_all_networks():
    to_search = get_all_package_names()
    return _get_networks(list(to_search))


@bp.route("/getNetwork/<package_name>", methods=["GET"])
def get_network(package_name: str):
    return _get_networks([package_name])


def format_as_nx(data: dict[str, PackageNode]):
    G = nx.DiGraph()
    for p in data.values():
        G.add_node(p.package_id)

    for p in data.values():
        if p.dependency_id_list:
            for d in p.dependency_id_list:
                G.add_edge(d, p.package_id)
    graph_data = nx.node_link_data(G)
    return graph_data


def format_for_frontend(data):
    nx_graph = format_as_nx(data)
    return jsonify(nx_graph)
