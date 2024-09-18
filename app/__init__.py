from typing import List
from flask import Flask, jsonify
from app.utils import utils
import networkx as nx

from app.utils.package import Package


def create_app():
    app = Flask(__name__)

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    @app.route("/npm")
    def npm():
        return jsonify(utils.utils.scrape_data())

    @app.route("/dependencies/<package_name>", methods=["GET"])
    def get_package_dependencies(package_name):
        data: List[Package] = utils.scrape_all_data()
        graph = utils.build_big_graph(data)
        # return {}
        # graph = utils.build_graph(package_name)

        graph_data = nx.node_link_data(graph)
        return jsonify(graph_data)

    # Configure our app here. if we want to use blueprints later, we can do that.
    return app
