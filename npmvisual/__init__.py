import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify
from neo4j import GraphDatabase

from config import Config
from npmvisual.extensions.neo4j_db import Neo4j
# from npmvisual.data import clear_cache

# from .extensions.flask_Native_Neo4j import FlaskNativeNeo4j
# from .utils import (
#     build_graph_ego_network,
#     build_popular_network,
#     scrape_all_data,
# )

# db = FlaskNativeNeo4j()
db = Neo4j()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    load_logs(app)

    db.init_app(app)

    from npmvisual.data import bp as data_bp

    app.register_blueprint(data_bp, url_prefix="/data")

    # @app.teardown_appcontext
    # def close_db(error):
    #     pass
    #     # db.close_db(error)

    # @app.route("/scrapeAll", methods=["GET"])
    # def scrape_all():
    #     scrape_all_data(1000)
    #     return "success"
    #

    # @app.route("/dependencies/<package_name>", methods=["GET"])
    # def get_package_dependencies(package_name):
    #     g = build_graph_ego_network(package_name)
    #     return jsonify(g)
    #
    # @app.route("/clearCache")
    # def clear_cache_route():
    #     # x = get_db()
    #     # print(x)
    #     clear_cache()
    #     return "success"
    #
    # @app.route("/getPopularNetwork")
    # def get_popular_network():
    #     g = build_popular_network()
    #     return jsonify(g)
    #
    # app.logger.info("app created")
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


def config_db(app):
    URI = (
        "neo4j://" + app.config["NEO4J_HOST"]
    )  # + ":" + current_app.config["NEO4J_PORT"]
    AUTH = (
        app.config["NEO4J_USERNAME"],
        app.config["NEO4J_PASSWORD"],
    )
    database = app.config["NEO4J_DB"]
    driver = GraphDatabase.driver(URI, auth=AUTH)
    return driver
