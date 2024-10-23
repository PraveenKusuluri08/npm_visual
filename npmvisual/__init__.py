import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify
from neo4j import GraphDatabase
from npmvisual.data import clear_cache

from .utils import (
    build_graph_ego_network,
    build_popular_network,
    scrape_all_data,
)
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    load_logs(app)

    URI = "neo4j://" + app.config["NEO4J_HOST"]  # + ":" + app.config["NEO4J_PORT"]
    AUTH = (app.config["NEO4J_USERNAME"], app.config["NEO4J_PASSWORD"])
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        print("db connection established")

    @app.route("/scrapeAll", methods=["GET"])
    def scrape_all():
        scrape_all_data(1000)
        return "success"

    @app.route("/dependencies/<package_name>", methods=["GET"])
    def get_package_dependencies(package_name):
        g = build_graph_ego_network(package_name)
        return jsonify(g)

    @app.route("/clearCache")
    def clear_cache_route():
        clear_cache()
        return "success"

    @app.route("/getPopularNetwork")
    def get_popular_network():
        g = build_popular_network()
        return jsonify(g)

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
