import logging
import os
import signal
import sys
from logging.handlers import RotatingFileHandler
import flask
from neo4j._sync.driver import GraphDatabase

from config import Config

# from npmvisual._models.neomodel_connection_test import NeomodelConnectionTest
from npmvisual.extensions.neo4j_db import Neo4j
import neomodel
import npmvisual.models

from neomodel import config, db
# db = Neo4j()


def create_driver():
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
    NEO4J_HOST = os.environ.get("NEO4J_HOST")
    NEO4J_DB = os.environ.get("NEO4J_DB")
    NEO4J_PORT = os.environ.get("NEO4J_PORT")

    # neomodel.db.set_connection(os.environ["NEO4J_BOLT_URL"])
    # Item(name="Something Something Dark Side").save()
    #
    if NEO4J_HOST and NEO4J_USERNAME and NEO4J_DB:
        URI = "neo4j://" + NEO4J_HOST  # + ":" + current_app.config["NEO4J_PORT"]
        AUTH = (NEO4J_USERNAME, NEO4J_PASSWORD)
        driver = GraphDatabase.driver(URI, auth=AUTH)
        return driver


# def create_an_item():
#         neomodel.db.set_connection(driver=driver)
#         x = NeomodelConnectionTest().save()


def create_app(config_class=Config):
    app = flask.Flask(__name__)
    app.config.from_object(config_class)
    load_logs(app)

    driver = create_driver()
    if driver:
        print(")00000000000000000000000000000")
        neomodel.db.set_connection(driver=driver)
    app.config.update(neomodel_db_NODE_CLASS_REGISTRY=db._NODE_CLASS_REGISTRY)
    # config.DATABASE_URL = os.environ["NEO4J_BOLT_URL"]

    # db.init_app(app)
    #
    # @app.teardown_appcontext
    # def teardown_db(exception):
    #     """Cleanup the database connection on app shutdown."""
    #     print("App teardown detected. removing db.")
    #     if db:
    #         db.teardown(exception)

    @app.route("/test")
    def test():
        npmvisual.models.neomodel.db._NODE_CLASS_REGISTRY = flask.current_app.config[
            "neomodel_db_NODE_CLASS_REGISTRY"
        ]

        x = npmvisual.models.NeomodelConnectionTest()
        x.save()
        print("kdkdddddddddddddddieeeeee")
        return "sdkkkkkkkkkkkkkkk"

        # import npmvisual.models
        #
        # x = npmvisual.models.NeomodelConnectionTest()
        # x.save()
        # return "success"

        # return flask.jsonify(
        #     {
        #         "items": [
        #             item.name for item in npmvisual.models.NeomodelConnectionTest.nodes
        #         ]
        #     }
        # )

    # @app.route("test")
    # def test():
    #     item = NeomodelConnectionTest()
    #
    #     from npmvisual import db
    #
    #     db.save(item)
    #     # item.save()
    #     print("success")

    #
    # Signal handler for graceful shutdown
    def handle_sigint(signal, frame):
        print("Shutting down gracefully...")
        if db.driver:  # Ensure the driver exists and is connected
            db.driver.close()
            print("db connection closed")
        sys.exit(0)

    # Register signal handler to catch the interrupt signal (Ctrl+C)
    signal.signal(signal.SIGINT, handle_sigint)
    #
    # from npmvisual.data import bp as data_bp
    #
    # app.register_blueprint(data_bp, url_prefix="/data")
    #
    # from npmvisual.graph import bp as graph_bp
    #
    # app.register_blueprint(graph_bp)
    #
    # from npmvisual.migrations import bp as migrations_bp
    #
    # app.register_blueprint(migrations_bp, url_prefix="/migrations")
    #
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
