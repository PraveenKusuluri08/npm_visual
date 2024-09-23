from typing import List
from flask import Flask, jsonify
from app.utils import utils
import networkx as nx

from app.utils.package import Package


def create_app():
    app = Flask(__name__)

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    @app.route("/scrapeSome", methods=["GET"])
    def scrape_some():
        utils.scrape_all_data()
        return "success"

    @app.route("/scrapeAll", methods=["GET"])
    def scrape_all():
        utils.scrape_all_data_long()
        return "success"

    @app.route("/npm")
    def npm():
        return jsonify(utils.utils.scrape_data())

    @app.route("/dependencies/<package_name>", methods=["GET"])
    def get_package_dependencies(package_name):
        # data: List[Package] = utils.scrape_all_data()
        graph = utils.build_graph(package_name)
        # return {}
        # graph = utils.build_graph(package_name)

        graph_data = nx.node_link_data(graph)
        return jsonify(graph_data)

    # Configure our app here. if we want to use blueprints later, we can do that.
    return app
