import logging
import os
import signal
import sys
from logging.handlers import RotatingFileHandler

from flask import Flask

from config import Config
from npmvisual.extensions.neo4j_db import Neo4j

db = Neo4j()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    load_logs(app)

    db.init_app(app)

    @app.teardown_appcontext
    def teardown_db(exception):
        "App teardown detected. removing db."
        if db:
            db.teardown(exception)

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

    from npmvisual.data import bp as data_bp

    app.register_blueprint(data_bp, url_prefix="/data")

    from npmvisual.graph import bp as graph_bp

    app.register_blueprint(graph_bp)

    from npmvisual.migrations import bp as migrations_bp

    app.register_blueprint(migrations_bp, url_prefix="/migrations")

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
