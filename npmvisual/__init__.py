import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify

from npmvisual.data.cache import clean_cache

from .utils import (
    build_graph_ego_network,
    scrape_all_data_long,
)


def create_app():
    app = Flask(__name__)
    load_logs(app)

    @app.route("/scrapeAll", methods=["GET"])
    def scrape_all():
        scrape_all_data_long()
        return "success"

    @app.route("/dependencies/<package_name>", methods=["GET"])
    def get_package_dependencies(package_name):
        g = build_graph_ego_network(package_name)
        return jsonify(g)

    @app.route("/cleanCache")
    def clean_cache_route():
        clean_cache()
        return "success"

    app.logger.info("app created")
    return app


def load_logs(app):
    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = RotatingFileHandler("logs/app.log", maxBytes=10240, backupCount=10)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
        )
    )
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("logger setup")
    return
