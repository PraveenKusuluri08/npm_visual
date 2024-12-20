# pyright: basic
import random
import leidenalg
import igraph as ig

import networkx as nx
from community import community_louvain
from flask import Blueprint, jsonify

import npmvisual.utils as utils
from npmvisual._models.packageNode import PackageNode
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

    (found, not_found) = search_and_scrape_recursive(set(package_names), max_count)
    print(f"Found: {len(found)} packages, Not Found: {len(not_found)}")

    if not_found:
        print(
            f"Successfully created network of size {len(found)}.\n"
            f"Failed to scrape or find: {not_found}"
        )

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


def format_as_nx(data: dict[str, PackageNode]):
    """
    Converts the given package data into a NetworkX graph and formats it into a structure
    with in-degrees and colors based on SCCs.

    Args:
        data: A dictionary of PackageNode objects where the key is the package ID and the
        value is the PackageNode.

    Returns:
        A dictionary in the node-link format with additional 'inDegree', 'val', and
        'color' properties for each node.
    """
    G: nx.DiGraph = nx.DiGraph()

    # Add edges to the graph
    for p in data.values():
        if p.dependency_id_list:
            for d in p.dependency_id_list:
                G.add_edge(d, p.package_id)

    # Prepare the graph data in node-link format
    graph_data = nx.node_link_data(G, edges="links")  # pyright: ignore
    graph_data = _add_val(graph_data, G, data)  # pyright: ignore
    graph_data = _color_nodes(graph_data, G, data)  # pyright: ignore

    # Return the graph data for frontend
    return graph_data


def _add_val(graph_data, G, data):
    # Get in-degrees for normalization
    largest_in_degree: int = 0  # Maximum in-degree encountered
    for p in data.values():  # pyright: ignore[reportUnknownVariableType]
        if p.dependency_id_list:  # pyright: ignore[reportUnknownMemberType]
            largest_in_degree = max(
                largest_in_degree,
                len(p.dependency_id_list),
            )
        in_degrees: dict[str, int] = dict(G.in_degree())
    for node in graph_data["nodes"]:  # pyright: ignore[reportUnknownVariableType]
        node_id: str = node["id"]  # pyright: ignore[reportUnknownVariableType]
        in_degree: int = in_degrees[node_id]
        node["inDegree"] = in_degree / largest_in_degree
        node["val"] = in_degree * 4
    return graph_data  # pyright: ignore[reportUnknownVariableType]


def _color_nodes(graph_data, G, data):
    undirected = G.copy().to_undirected()
    #
    # # Create a dictionary to assign a color to each component
    # component_colors: dict[int, str] = {
    #     i: f"#{random.randint(0, 0xFFFFFF):06x}" for i in range(len(sccs))
    # }
    communities = nx.community.louvain_communities(undirected)
    node_colors = {}
    default_color = f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"
    for i, community in enumerate(communities):
        print(f"Community {i+1}: {community}")
        if len(community) > 1:
            color = f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"
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
    # G_igraph = ig.Graph.from_networkx(G)
    # # Apply Leiden algorithm for community detection
    # partition = leidenalg.find_partition(G_igraph, leidenalg.ModularityVertexPartition)
    # # Create a dictionary to store community assignments for each node
    # node_to_community: dict[str, int] = {}
    # print(graph.nodes)
    # # Assign each node to a community (from the partition)
    # for community_idx, community in enumerate(partition):
    #     for node in community:
    #         # Assuming `node` is an integer index, and you want to map it to `package_id`
    #         print(node)
    #         # node_id = G.nodes[node]["id"]  # Replace with your mapping logic if needed
    #         # node_to_community[node_id] = community_idx
    #
    # print(node_to_community)


"""
def format_as_nx(data: dict[str, PackageNode]):
    largest_in_degree = 0
    G = nx.DiGraph()

    for p in data.values():
        if p.dependency_id_list:
            largest_in_degree = max(largest_in_degree, len(p.dependency_id_list))
            for d in p.dependency_id_list:
                G.add_edge(d, p.package_id)


    # analyzer.analyze(G)
    graph_data = nx.node_link_data(G)
    in_degrees: nx.classes.reportviews.InDegreeView = G.in_degree()
    print(type(in_degrees))
    for node in graph_data["nodes"]:
        id = node["id"]
        in_degree: int = in_degrees[id]
        node["inDegree"] = in_degree / largest_in_degree
        node["val"] = in_degree / largest_in_degree
        node["val"] = in_degree * 4

    # print(f"Graph data for frontend: {graph_data}")
    return graph_data
    """


def format_for_frontend(data):
    nx_graph = format_as_nx(data)
    return jsonify(nx_graph)
