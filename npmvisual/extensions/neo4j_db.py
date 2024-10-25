from flask.app import Flask
from neo4j import GraphDatabase, Session


class Neo4j:
    app: Flask | None

    def __init__(self):
        self.app = None
        self.driver: Session | None = None

    def init_app(self, app):
        self.app = app
        app.n4j = self  # type: ignore
        if "neo4j" in app.extensions:
            raise RuntimeError(
                "A 'neo4j' instance has already been registered on this Flask app."
                " Import and use that instance instead."
            )
        app.extensions["neo4j"] = self

        self.config = app.config
        self._connect()

    def _connect(self):
        URI = (
            "neo4j://" + self.config["NEO4J_HOST"]
        )  # + ":" + current_app.config["NEO4J_PORT"]
        AUTH = (
            self.config["NEO4J_USERNAME"],
            self.config["NEO4J_PASSWORD"],
        )
        database = self.config["NEO4J_DB"]
        driver = GraphDatabase.driver(URI, auth=AUTH)
        driver.verify_connectivity()
        print("db connection established")
        self.driver = driver.session(database=database)
        return self.driver

    def get_db(self):
        if not self.driver:
            return self._connect()
        return self.driver

    def teardown(self, exception):
        if self.driver:
            self.driver.close()
            print("db connection closed")
