from flask import g
from flask import current_app

from neo4j import GraphDatabase


class FlaskDBExtension:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        x = 0

        if hasattr(app, "teardown_appcontext"):
            app.teardown_appcontext(self.teardown)

    @property
    def connect(self):
        if not hasattr(g, "neo4j_db"):
            URI = (
                "neo4j://" + current_app.config["NEO4J_HOST"]
            )  # + ":" + current_app.config["NEO4J_PORT"]
            AUTH = (
                current_app.config["NEO4J_USERNAME"],
                current_app.config["NEO4J_PASSWORD"],
            )
            database = current_app.config["NEO4J_DB"]
            with GraphDatabase.driver(URI, auth=AUTH) as driver:
                driver.verify_connectivity()
            print("db connection established")
            g.neo4j_db = driver.session(database=database)
        return g.neo4j_db

    @property
    def connection(self):
        """Attempts to connect to the MySQL server.

        :return: Bound MySQL connection object if successful or ``None`` if
            unsuccessful.
        """

        if g is not None:
            if not hasattr(g, "mysql_db"):
                g.mysql_db = self.connect
            return g.mysql_db

    def teardown(self, exception):
        if hasattr(g, "mysql_db"):
            g.mysql_db.close()
