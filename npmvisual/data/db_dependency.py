from neo4j.graph import Node, Relationship

from npmvisual import db
from npmvisual.models import Dependency


def get_dependencies_from_db(package_name: str) -> list[Dependency]:
    # print(f"searching for package in db: {package_name}")

    def match_dependency_tx(tx):
        result = tx.run(
            """
            MATCH (
                p:Package {package_id : $package_id }
            )-[d]->(q)
            RETURN d, q
            """,
            package_id=package_name,
        )
        dependencies: list[Relationship] = [
            record["d"] for record in result
        ]  # Consume the results here
        return dependencies

    records = db.execute_read(match_dependency_tx)
    if records is None:
        return []

    dependencies: list[Dependency] = []
    record: Relationship
    for record in records:
        # print(f"\tdependency: {record}")
        n2: Node = record.end_node
        other_package_name = n2.get("package_id")
        version = record.get("version")
        d = Dependency(other_package_name, version)
        dependencies.append(d)

    return dependencies


def db_dependency_merge(package_id: str, dependency: Dependency):
    print(f"\t\tDependency merge for {dependency}")

    # todo: {version: $version}
    def dependency_merge_tx(tx):
        return tx.run(
            """
        MATCH (a {package_id: $a_id}), 
                (b {package_id: $b_id})
        MERGE (a)-[d:DependsOn ]->(b)
        ON CREATE SET 
            a.created = timestamp(),
            b.created = timestamp(),
            d.created = timestamp()
        ON MATCH SET
            a.counter = coalesce(a.counter, 0) + 1,
            a.accessTime = timestamp(),
            b.counter = coalesce(a.counter, 0) + 1,
            b.accessTime = timestamp(),
            d.counter = coalesce(a.counter, 0) + 1,
            d.accessTime = timestamp()
        RETURN d,a,b
        """,
            a_id=package_id,
            b_id=dependency.package,
            version=dependency.version,
        )

    x = db.execute_write(dependency_merge_tx)
    # print(x)
    return x
