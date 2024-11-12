# __init__.py
from config import Config
import os
import signal
import sys
import flask
from neo4j._sync.driver import GraphDatabase
import neomodel
import npmvisual.models
from neomodel import config, db
from npmvisual.extensions.neo4j_db import Neo4j

# n4j = Neo4j()

NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
NEO4J_HOST = os.environ.get("NEO4J_HOST")
NEO4J_DB = os.environ.get("NEO4J_DB")
NEO4J_PORT = os.environ.get("NEO4J_PORT", "7687")  # default to 7687 if not set

NEO4J_BOLT_URL = f"bolt://{NEO4J_USERNAME}:{NEO4J_PASSWORD}@localhost:7687"
config.DATABASE_URL = NEO4J_BOLT_URL

x = npmvisual.models.NeomodelConnectionTest()
x.save()
print("00000")
# if NEO4J_HOST and NEO4J_USERNAME and NEO4J_PASSWORD:
#     URI = f"neo4j://{NEO4J_HOST}:{NEO4J_PORT}"
#     AUTH = (NEO4J_USERNAME, NEO4J_PASSWORD)
#     try:
#         my_driver = GraphDatabase.driver(
#             URI, auth=AUTH, encrypted=False
#         )  # Disable encryption (SSL)
#         # Use the Flask app context to bind the driver to neomodel
#         neomodel.db.set_connection(driver=my_driver)
#         my_db = neomodel.db
#         print("Neo4j connection established")
#     except Exception as e:
#         print(f"Failed to connect to Neo4j: {e}")
#         raise


def create_app(config_class=Config):
    app = flask.Flask(__name__)
    app.config.from_object(config_class)
    # n4j.init_app(app)
    print("33333333")

    # Initialize Neo4j driver only within the app context
    # Set Flask app config
    # app.config.update(neomodel_db_NODE_CLASS_REGISTRY=db._NODE_CLASS_REGISTRY)

    @app.route("/test")
    def test():
        # # Ensure the Flask app context is used here
        # npmvisual.models.neomodel.db._NODE_CLASS_REGISTRY = flask.current_app.config[
        #     "neomodel_db_NODE_CLASS_REGISTRY"
        # ]
        #
        # # Now the model can be instantiated and saved
        x = npmvisual.models.NeomodelConnectionTest(name="testing")
        x.save()
        print(x)

        recent_objects = npmvisual.models.NeomodelConnectionTest.nodes.order_by(
            "-created_at"
        )[:10]
        for test in recent_objects:
            print(test)
        #

        return "Node saved successfully!"

    # Signal handler for graceful shutdown
    def handle_sigint(signal, frame):
        print("Shutting down gracefully...")
        if db.driver:  # Ensure the driver exists and is connected
            db.driver.close()
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
