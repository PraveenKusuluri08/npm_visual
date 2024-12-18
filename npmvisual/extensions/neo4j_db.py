import logging
import os
from collections.abc import Callable
from typing import Concatenate, Final

from flask.app import Flask
from neo4j import GraphDatabase
from neo4j._sync.driver import Driver
from neo4j._sync.work.transaction import ManagedTransaction
from neomodel import config as neomodel_config
from typing_extensions import ParamSpec, TypeVar

import npmvisual.models
from config import Config

# from graphdatascience import GraphDataScience

P = ParamSpec("P")
R = TypeVar("R")


class Neo4j_Connection:
    app: Flask | None = None
    config: Config | None = None
    driver: Driver | None = None
    neo4j_username: Final[str]
    neo4j_password: Final[str]
    neo4j_host: Final[str]
    neo4j_db: Final[str]
    neo4j_port: Final[str]
    neo4j_bolt_url: Final[str]

    def __init__(self, config_class=Config):
        self.neo4j_username = config_class.NEO4J_USERNAME
        self.neo4j_password = config_class.NEO4J_PASSWORD
        self.neo4j_host = config_class.NEO4J_HOST
        self.neo4j_db = config_class.NEO4J_DB
        self.neo4j_port = os.environ.get("NEO4J_PORT", "7687")

        self.neo4j_bolt_url = (
            f"bolt://{self.neo4j_username}:{self.neo4j_password}@localhost:7687"
        )
        neomodel_config.DATABASE_URL = self.neo4j_bolt_url
        self._init_connection()

    def _init_connection(self):
        """This exists so that neomodel will be on the same thread. This function must be
        called before flask is created"""
        important_do_not_delete = npmvisual.models.NeomodelConnectionTest()
        important_do_not_delete.save()

    def init_app(self, app):
        self.app = app
        app.n4j = self  # type: ignore
        if "neo4j" in app.extensions:
            raise RuntimeError(
                "A 'neo4j' instance has already been registered on this Flask app."
                + " Import and use that instance instead."
            )
        app.extensions["neo4j"] = self

        self.config = app.config
        self._connect()

        app.teardown_appcontext(self.teardown)

    def _connect(self):
        uri = "neo4j://" + self.neo4j_host  # + ":" + current_app.config["NEO4J_PORT"]
        auth = (self.neo4j_username, self.neo4j_password)
        self.uri = uri
        self.auth = auth
        self.database = self.neo4j_db
        self.driver = GraphDatabase.driver(uri, auth=auth)

        # Configure Neomodel connection to use the same driver
        self._verify_connectivity()

        # gds = GraphDataScience(URI, AUTH)
        # print(gds.version())
        # assert gds.version()
        return self.driver

    def _verify_connectivity(self):
        # Ensure the connection is working
        try:
            if self.driver:
                self.driver.verify_connectivity()
                logging.info("Neo4j connection established.")
        except Exception as e:
            logging.error(f"Error connecting to Neo4j: {e}")
            raise

    def get_driver(self):
        if not self.driver:
            return self._connect()
        return self.driver

    def teardown(self, exception):
        print(f"closing db. exception: {exception}")
        if self.driver:
            self.driver.close()
            print("db connection closed for driver")

    def run(self, command):
        assert self.driver is not None, "Driver is not initialized!"
        with self.driver.session(database=self.database) as session:
            return session.run(command)

    def execute_read(
        self,
        transaction_function: Callable[Concatenate[ManagedTransaction, P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        """
        A very thin wrapper around the Neo4j execute_read. All the Parameters and return
        types should be identical.

        This is needed because sessions are used short term, and there won't be a single
        session for the flask app to access.
        """
        with self.driver.session(database=self.database) as session:
            return session.execute_read(transaction_function, *args, **kwargs)

    def execute_write(
        self,
        transaction_function: Callable[Concatenate[ManagedTransaction, P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        """
        A very thin wrapper around the Neo4j execute_write. All the Parameters and return
        types should be identical.

        This is needed because sessions are used short term, and there won't be a single
        session for the flask app to access.
        """
        with self.driver.session(database=self.database) as session:
            return session.execute_write(transaction_function, *args, **kwargs)
