import networkx as nx
from flask import Blueprint, jsonify, request

import npmvisual.utils as utils
from npmvisual._models.packageNode import PackageNode
from npmvisual.commonpackages import get_popular_package_names
from npmvisual.data import (
    search_and_scrape_recursive,
)

bp = Blueprint("network", __name__)


@bp.route("/getNetworks/<package_names>", methods=["GET"])
def get_networks(package_names: list[str]):  # todo add type
    package_names = request.args.get("package_names", "").split(",")
    if not package_names:
        return jsonify({"error": "No package names provided"}), 400

    return _get_networks(package_names)


def _get_networks(package_names: list[str], max_count: int | utils.Infinity = utils.infinity):
    print(f"Fetching network for packages: {package_names}")
    
    (found, not_found) = search_and_scrape_recursive(
        set(package_names), max_count
    )
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
    return _get_networks(list(to_search), max_count=1000)


@bp.route("/getAllNetworks", methods=["GET"])
def get_all_networks():
    to_search = utils.get_all_package_names()
    return _get_networks(list(to_search))


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

        G = nx.DiGraph() if graph_data.get("directed", True) else nx.Graph()
        for node in graph_data["nodes"]:
            G.add_node(node["id"])
        
        for link in graph_data["links"]:
            G.add_edge(link["source"], link["target"])
        
        degree_centrality = nx.degree_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G, normalized=True, endpoints=True)

        analysis_results = {
            "degree_centrality": degree_centrality,
            "betweenness_centrality": betweenness_centrality
        }
        
        print("Analysis Results:", analysis_results)
        
        return jsonify(analysis_results), 200

    except Exception as e:
        print(f"Error processing the request for {package_name}: {str(e)}")
        return jsonify({"error": str(e)}), 500

def format_as_nx(data: dict[str, PackageNode]):
    G = nx.DiGraph()
    for p in data.values():
        G.add_node(p.package_id)

    for p in data.values():
        if p.dependency_id_list:
            for d in p.dependency_id_list:
                G.add_edge(d, p.package_id)
                
    print(f"Nodes in the graph: {list(G.nodes)}")
    print(f"Edges in the graph: {list(G.edges)}")
    
    graph_data = nx.node_link_data(G)
    print(f"Graph data for frontend: {graph_data}")
    return graph_data


def format_for_frontend(data):
    nx_graph = format_as_nx(data)
    return jsonify(nx_graph)
