from neo4j import GraphDatabase

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
