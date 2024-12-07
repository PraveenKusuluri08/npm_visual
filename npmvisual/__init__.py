import logging
import os
import signal
import sys
from logging.handlers import RotatingFileHandler

import flask
from neomodel import db as neomodel_db

from config import Config
from npmvisual.extensions.neo4j_db import Neo4j

# make outside of flask to be ouside of flask context
db = Neo4j(config_class=Config)


def create_app(config_class=Config):
    app = flask.Flask(__name__)
    app.config.from_object(config_class)
    load_logs(app)
    # activate extensions after flask exists to tell db manager how to connect to it.
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
