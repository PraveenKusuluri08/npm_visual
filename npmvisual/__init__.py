from typing import Dict

import networkx as nx
from flask import Flask, jsonify

from .package import Package
from .utils import build_big_graph, scrape_all_data_long, scrape_data


def create_app():
    app = Flask(__name__)

    @app.route("/scrapeSome", methods=["GET"])
    def scrape_some():
        scrape_some()  # scrape_all_data()
        return "success"

    @app.route("/scrapeAll", methods=["GET"])
    def scrape_all():
        scrape_all_data_long()
        return "success"

    @app.route("/dependencies/<package_name>", methods=["GET"])
    def get_package_dependencies(package_name):
        packages = [package_name]
        data: Dict[str, Package] = scrape_data(packages)
        graph = build_big_graph(data)
        graph_data = nx.node_link_data(graph)
        return jsonify(graph_data)

    # Configure our app here. if we want to use blueprints later, we can do that.
    return app
