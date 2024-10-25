# from flask import current_app, g
# from flask.app import Flask
# from neo4j import GraphDatabase
#
#
# class FlaskNativeNeo4j:
#     def __init__(self, app=None):
#         self.app = app
#         if app is not None:
#             self.init_app(app)
#             print("flask.ext.FlaskNativeNeo4j init_app called")
#
#     def init_app(self, app: Flask):
#         """Initialize the `app` for use with this :class:`~Neo4j`. This is
#         called automatically if `app` is passed to :meth:`~Neo4j.__init__`.
#
#         The app is configured according to these configuration variables
#         ``CONNECTION_RETRY``
#         ``RETRY_INTERVAL``
#
#         :param flask.Flask app: the application configured for use with
#            this :class:`~Neo4j`
#         """
#
#         self.app = app
#         app.n4j = self  # type: ignore
#
#         if "neo4j" in app.extensions:
#             raise RuntimeError(
#                 "A 'neo4j' instance has already been registered on this Flask app."
#                 " Import and use that instance instead."
#             )
#         app.extensions["neo4j"] = self
#
#         # Use the newstyle teardown_appcontext if it's available,
#         # otherwise fall back to the request context
#         if hasattr(app, "teardown_appcontext"):
#             app.teardown_appcontext(self.teardown)
#         else:
#             app.teardown_request(self.teardown)
#
#     @property
#     def driver(self):
#         if not hasattr(g, "neo4j_db"):
#             URI = (
#                 "neo4j://" + current_app.config["NEO4J_HOST"]
#             )  # + ":" + current_app.config["NEO4J_PORT"]
#             AUTH = (
#                 current_app.config["NEO4J_USERNAME"],
#                 current_app.config["NEO4J_PASSWORD"],
#             )
#             database = current_app.config["NEO4J_DB"]
#             with GraphDatabase.driver(URI, auth=AUTH) as driver:
#                 driver.verify_connectivity()
#             print("db connection established")
#             g.neo4j_db = driver.session(database=database)
#         return g.neo4j_db
#
#     @property
#     def connection(self):
#         """Attempts to connect to the Neoserver.
#
#         :return: Bound neo4j connection object if successful or ``None`` if
#             unsuccessful.
#         """
#
#         if g is not None:
#             if not hasattr(g, "neo4j_db"):
#                 g.neo4j_db = self.driver
#             return g.neo4j_db
#
#     def teardown(self, exception):
#         if hasattr(g, "neo4j_db"):
#             g.neo4j_db.close()
