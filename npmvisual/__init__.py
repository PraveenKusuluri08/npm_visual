import logging
from logging.handlers import RotatingFileHandler
from config import Config
import os
import signal
import sys
import flask
import npmvisual.models
from neomodel import config, db as neomodel_db
from npmvisual.extensions.neo4j_db import Neo4j

db = Neo4j()

NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
NEO4J_HOST = os.environ.get("NEO4J_HOST")
NEO4J_DB = os.environ.get("NEO4J_DB")
NEO4J_PORT = os.environ.get("NEO4J_PORT", "7687")  # default to 7687 if not set

NEO4J_BOLT_URL = f"bolt://{NEO4J_USERNAME}:{NEO4J_PASSWORD}@localhost:7687"
config.DATABASE_URL = NEO4J_BOLT_URL

x = npmvisual.models.NeomodelConnectionTest()
x.save()


def create_app(config_class=Config):
    app = flask.Flask(__name__)
    app.config.from_object(config_class)
    load_logs(app)
    db.init_app(app)

    def handle_sigint(signal, frame):
        print("Shutting down gracefully...")
        if neomodel_db.driver:  # Ensure the driver exists and is connected
            neomodel_db.driver.close()
            print("db connection closed")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    from npmvisual.data import bp as data_bp

    app.register_blueprint(data_bp, url_prefix="/data")

    from npmvisual.graph import bp as graph_bp

    app.register_blueprint(graph_bp)

    from npmvisual.migrations import bp as migrations_bp

    app.register_blueprint(migrations_bp, url_prefix="/migrations")

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
