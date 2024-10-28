from npmvisual import db
from npmvisual.data import bp
from npmvisual.data.db_package import (
    db_network_search,
    db_package_delete_all,
    db_recursive_network_search,
)


@bp.route("/test", methods=["GET"])
def open_db():
    print(db)
    x = db.driver
    print(x)
    return "test"
    # get_db()


@bp.route("/network")
def network():
    db_recursive_network_search()
    # db_package_delete_all()
    return "success"


@bp.route("/deletePackages")
def delete_packages():
    db_package_delete_all()
    return "success"


#
# def get_db():
#     if not hasattr(g, "neo4j_db"):
#         URI = "neo4j://" + app.config["NEO4J_HOST"]  # + ":" + app.config["NEO4J_PORT"]
#         AUTH = (app.config["NEO4J_USERNAME"], app.config["NEO4J_PASSWORD"])
#         database = app.config["NEO4J_DB"]
#         with GraphDatabase.driver(URI, auth=AUTH) as driver:
#             driver.verify_connectivity()
#         print("db connection established")
#         g.neo4j_db = driver.session(database=database)
#     return g.neo4j_db
#
#
# def close_db(error):
#     if hasattr(g, "neo4j_db"):
#         g.neo4j_db.close()
#

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
# URI = "<URI for Neo4j database>"
# AUTH = ("<Username>", "<Password>")
#
# with GraphDatabase.driver(URI, auth=AUTH) as driver:
#     driver.verify_connectivity()

# graph = Graph()
# def create_uniqueness_constraint(label, property):
#     query = "CREATE CONSTRAINT ON (n:{label}) ASSERT n.{property} IS UNIQUE"
#     query = query.format(label=label, property=property)
#     graph.cypher.execute(query)
#
#
# def constrain_package():
#     create_uniqueness_constraint("package", "id")
