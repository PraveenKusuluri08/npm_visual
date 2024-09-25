from flask import Flask, jsonify

from npmvisual.scraper import scrape_all_data_long, scrape_package_ego_network

from .utils import build_graph_ego_network


def create_app():
    app = Flask(__name__)

    @app.route("/scrapeAll", methods=["GET"])
    def scrape_all():
        scrape_all_data_long()
        return "success"

    @app.route("/dependencies/<package_name>", methods=["GET"])
    def get_package_dependencies(package_name):
        g = build_graph_ego_network(package_name)
        return jsonify(g)

    # Configure our app here. if we want to use blueprints later, we can do that.
    return app
