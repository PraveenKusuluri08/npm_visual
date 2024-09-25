from typing import Dict

import networkx as nx
from flask.json import jsonify

from npmvisual.scraper import scrape_package_ego_network

from .package import Package


def build_graph(packages: Dict[str, Package]):
    G = nx.DiGraph()
    for p in packages.values():
        # print(p)
        G.add_node(p.id)

    for p in packages.values():
        for e in p.dependencies:
            G.add_edge(e, p.id)
    return G


def build_graph_ego_network(package_name: str):
    packages = [package_name]
    data: Dict[str, Package] = scrape_package_ego_network(packages)
    graph = build_graph(data)
    graph_data = nx.node_link_data(graph)
    return graph_data
