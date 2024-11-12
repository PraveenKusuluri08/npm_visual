import functools
import logging
from typing import Callable, Concatenate, ParamSpec, TypeVar

from graphdatascience import GraphDataScience
from flask.app import Flask
from neo4j import GraphDatabase
from neo4j._sync.driver import Driver
from neo4j._sync.work.transaction import ManagedTransaction
from typing_extensions import Concatenate, ParamSpec

import neomodel
from neomodel import config as neomodel_config
from neomodel import db as neomodel_db

P = ParamSpec("P")
R = TypeVar("R")


class Neo4j:
    app: Flask | None

    # def session_run(
    #     f: (**P) -> R
    # )-> (bool, **P) -> R:
    #     def
    #     pass
    #

    def __init__(self):
        self.app = None
        self.driver: Driver
        self.driver2: Driver

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

        app.teardown_appcontext(self.teardown)

    def _connect(self):
        URI = (
            "neo4j://" + self.config["NEO4J_HOST"]
        )  # + ":" + current_app.config["NEO4J_PORT"]
        AUTH = (
            self.config["NEO4J_USERNAME"],
            self.config["NEO4J_PASSWORD"],
        )
        self.URI = URI
        self.AUTH = AUTH
        self.database = self.config["NEO4J_DB"]
        self.driver = GraphDatabase.driver(URI, auth=AUTH)

        self.verify_connectivity()  # Configure Neomodel connection to use the same driver

        # https://neomodel.readthedocs.io/en/stable/configuration.html

        # gds = GraphDataScience(URI, AUTH)
        # print(gds.version())
        # assert gds.version()
        # import neomodel
        # from neomodel import config as neomodel_config

        # neomodel_config.DRIVER = self.driver
        self.neomodel_db = neomodel_db
        self.neomodel_config = neomodel_config
        self.neomodel = neomodel
        neomodel_db.set_connection(driver=self.driver)
        return self.driver

    def verify_connectivity(self):
        # Ensure the connection is working
        try:
            self.driver.verify_connectivity()
            logging.info("Neo4j connection established.")
        except Exception as e:
            logging.error(f"Error connecting to Neo4j: {e}")
            raise

    def get_driver(self):
        if not self.driver:
            return self._connect()
        return self.driver

    def get_config(self):
        return self.neomodel_config

    def get_db(self):
        return self.neomodel_db

    def teardown(self, exception):
        print(f"closing db. exception: {exception}")
        if self.driver:
            print(self.driver)
            assert neomodel_db == self.neomodel_db

            if neomodel_db:
                print("neomodel_db exists")
            if self.neomodel_db:
                print("self.neomodel_db exists")

            if neomodel_db:
                neomodel_db.close_connection()
                print("closed neomodel_db")
            # if self.neomodel_db:
            #     neomodel_db.close_connection()
            self.driver.close()
            print("db connection closed for driver")

    def run(self, command):
        assert self.driver is not None, "Driver is not initialized!"
        with self.driver.session(database=self.database) as session:
            return session.run(command)

    # @session_run
    # def execute_write()

    # def execute_write(
    #     self,
    #     transaction_function: t.Callable[
    #         te.Concatenate[ManagedTransaction, _P], t.Union[_R]
    #     ],
    #     *args: _P.args,
    #     **kwargs: _P.kwargs,
    # ) -> _R:

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

    def save(self, neomodelClass):
        print("3333333333333333333 save called 33333333333333333333")
        # neomodel_db.set_connection(driver=self.driver)

        # with self.driver.session(database=self.database) as session:
        neomodelClass.save()

        print("44444444444444 save ended 33333333333333333333")
        # neomodel_db.close_connection()
