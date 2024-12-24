# pyright: basic
import math
import random

import networkx as nx
from flask import Blueprint, jsonify

import npmvisual.utils as utils
from npmvisual._models.package import Package, PackageData
from npmvisual.commonpackages import get_popular_package_names
from npmvisual.data import (
    get_db_all,
    search_and_scrape_recursive,
)

bp = Blueprint("network", __name__)


@bp.route("/getNetworks/<package_names>", methods=["GET"])
def get_networks(package_names: str):  # todo add type
    as_list = package_names.split(",")
    # print(f"as_list: {as_list}")
    if not package_names:
        return jsonify({"error": "No package names provided"}), 400
    return _get_networks(as_list)


def _get_networks(
    package_names: list[str], max_count: int | utils.Infinity = utils.infinity
):
    print(f"Fetching network for packages: {package_names}")

    found: dict[str, PackageData] = search_and_scrape_recursive(
        set(package_names), max_count
    )
    print(f"Found: {len(found)} packages, Not Found: {-1}")

    # if not_found:
    #     print(
    #         f"Successfully created network of size {len(found)}.\n"
    #         f"Failed to scrape or find: {not_found}"
    #     )

    formatted_data = format_for_frontend(found)
    print(f"Formatted graph data: {formatted_data}")
    return formatted_data


@bp.route("/getPopularNetworks", methods=["GET"])
def get_popular_networks():
    to_search = get_popular_package_names()
    return _get_networks(list(to_search), max_count=10000)


@bp.route("/getAllNetworks", methods=["GET"])
def get_all_networks():
    to_search = utils.get_all_package_names()
    return _get_networks(list(to_search))


@bp.route("/getAllDBNetworks", methods=["GET"])
def get_all_db_networks():

    print("Getting all nodes in the db")
    found = get_db_all()
    print(f"Got all nodes in the db: {len(found)} packages")

    formatted_data = format_for_frontend(found)
    print(f"Formatted graph data: {formatted_data}")
    return formatted_data


@bp.route("/getNetwork/<package_name>", methods=["GET"])
def get_network(package_name: str):
    return _get_networks([package_name])


@bp.route("/analyzeNetwork/<package_name>", methods=["GET"])
def analyze_network(package_name: str):
    try:
        response = _get_networks([package_name])
        graph_data = response.get_json()

        if not graph_data:
            return jsonify({"error": "No graph data provided"}), 400
        if "nodes" not in graph_data or "links" not in graph_data:
            return jsonify({"error": "Invalid graph structure"}), 400

        G: DiGraph = nx.DiGraph()
        for node in graph_data["nodes"]:
            G.add_node(node["id"])

        for link in graph_data["links"]:
            G.add_edge(link["source"], link["target"])

        degree_centrality = nx.degree_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(
            G, normalized=True, endpoints=True
        )

        analysis_results = {
            "degree_centrality": degree_centrality,
            "betweenness_centrality": betweenness_centrality,
        }

        print("Analysis Results:", analysis_results)

        return jsonify(analysis_results), 200

    except Exception as e:
        print(f"Error processing the request for {package_name}: {str(e)}")
        return jsonify({"error": str(e)}), 500


def format_as_nx(data: dict[str, PackageData]):
    """
    Converts the given package data into a NetworkX graph and formats it into a structure
    with in-degrees and colors based on SCCs.

    Args:
        data: A dictionary of Package objects where the key is the package ID and the
        value is the Package.

    Returns:
        A dictionary in the node-link format with additional 'inDegree', 'val', and
        'color' properties for each node.
    """
    G: nx.DiGraph = nx.DiGraph()

    for p in data.values():
        for d in p.dependencies:
            # G.add_edge(p.package.package_id, d.package_id)
            G.add_edge(d.package_id, p.package.package_id)

    # Prepare the graph data in node-link format
    graph_data = nx.node_link_data(G, edges="links")
    graph_data = _add_val(graph_data, G, data)
    graph_data = _color_nodes(graph_data, G, data)

    # Return the graph data for frontend
    return graph_data


def _add_val(graph_data, G, data: dict[str, PackageData]):
    # Get in-degrees for normalization
    largest_in_degree: int = 0
    for p in data.values():
        largest_in_degree = max(
            largest_in_degree,
            len(p.dependencies),
        )
    in_degrees: dict[str, int] = dict(G.in_degree())

    # Set the base size multiplier (you can adjust this to control overall size)
    size_exponent = 1.15
    size_multiplier = 5  # Adjust this to fine-tune node size scaling

    # Loop over nodes and apply stronger exponential scaling
    for node in graph_data["nodes"]:  # pyright: ignore[reportUnknownVariableType]
        node_id: str = node["id"]  # pyright: ignore[reportUnknownVariableType]
        in_degree: int = in_degrees[node_id]

        node["inDegree"] = in_degree

        # Apply stronger exponential scaling
        # Using in_degree**2 (quadratic scaling) for more drastic size differences
        node["val"] = (
            in_degree**size_exponent
        ) * size_multiplier  # Apply quadratic scaling

    return graph_data  # pyright: ignore[reportUnknownVariableType]


def _color_nodes(graph_data, G, data: dict[str, PackageData]):
    undirected = G.copy().to_undirected()
    #
    # # Create a dictionary to assign a color to each component
    # component_colors: dict[int, str] = {
    #     i: f"#{random.randint(0, 0xFFFFFF):06x}" for i in range(len(sccs))
    # }
    communities = nx.community.louvain_communities(undirected)
    node_colors = {}
    default_color = _get_random_color()
    for i, community in enumerate(communities):
        print(f"Community {i+1}: {community}")
        if len(community) > 1:
            color = _get_random_color()
            for community_id, node in enumerate(community):
                node_colors[node] = (color, community_id)
        else:
            for node in community:
                node_colors[node] = (default_color, -1)

    print(graph_data["nodes"])
    for node in graph_data["nodes"]:
        node["color"] = node_colors[node["id"]][0]
        node["color_id"] = node_colors[node["id"]][1]
        print(f"    node: {node}")

    return graph_data


def _get_random_color():
    """Generates a random color in hex format."""
    return f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"


def format_for_frontend(data: dict[str, PackageData]):
    nx_graph = format_as_nx(data)
    return jsonify(nx_graph)
