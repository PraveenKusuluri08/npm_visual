from neo4j.graph import Node, Relationship
import pprint
from npmvisual import db
from npmvisual._models.package import Package, prettyPrint
from npmvisual._models.package_version import PackageVersion
from npmvisual.models import Dependency
from neo4j._sync.work.result import Result


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


def db_merge_package_full(package: PackageVersion):
    print("Adding package version to DB")
    # print(f"package={package}")
    package.prettyPrint()

    # Function to execute the Cypher query to merge the package into the database
    def _merge_package_tx(tx):
        query_result: Result = tx.run(
            """
            MERGE (a:PackageVersion
                {
                    package_id: $package.id
                })
            ON CREATE SET
                a.created = timestamp(),
                a.created = COALESCE(a.created, timestamp()),

                a.description = $package.description,
                a.latest_version = $package.version,
                a.from_package = $package.from_package,
                a.package_id = $package.id,
                a.nodeVersion = $package._nodeVersion,
                a.npm_operational_internal_host = $package.npm_operational_internal.host,
                a.npm_operational_internal_tmp = $package.npm_operational_internal.tmp,
                a.npm_user_email = $package._npm_user.email,
                a.npm_user_name = $package._npm_user.name,
                a.npm_version = $package._npm_version,
                a.resolved = $package._resolved,
                a.shasum = $package._shasum,
                a.bin_ng_xi18n = $package.bin.ng_xi18n,
                a.bin_ngc = $package.bin.ngc,
                a.bugs_url = $package.bugs.url,
                a.homepage = $package.homepage,
                a.license = $package.license,
                a.main = $package.main,
                a.typings = $package.typings,
                a.keywords = $package.keywords,
                a.repository_type = $package.repository.type,
                a.repository_url = $package.repository.url,
                a.peerDependencies = $package.peerDependencies,
                a.dist_integrity = $package.dist.integrity,
                a.dist_shasum = $package.dist.shasum,
                a.dist_tarball = $package.dist.tarball,
                a.maintainers = $package.maintainers,
                a.contributors = $package.contributors


            ON MATCH SET
                a.counter = coalesce(a.counter, 0) + 1,
                a.accessTime = timestamp(),

                a.description = $package.description,
                a.latest_version = $package.version,
                a.created = COALESCE(a.created, timestamp()),
                a.from_package = $package.from_package,
                a.package_id = $package.id,
                a.nodeVersion = $package._nodeVersion,
                a.npm_operational_internal_host = $package.npm_operational_internal.host,
                a.npm_operational_internal_tmp = $package.npm_operational_internal.tmp,
                a.npm_user_email = $package._npm_user.email,
                a.npm_user_name = $package._npm_user.name,
                a.npm_version = $package._npmVersion,
                a.resolved = $package._resolved,
                a.shasum = $package._shasum,
                a.bin_ng_xi18n = $package.bin.ng_xi18n,
                a.bin_ngc = $package.bin.ngc,
                a.bugs_url = $package.bugs.url,
                a.homepage = $package.homepage,
                a.license = $package.license,
                a.main = $package.main,
                a.typings = $package.typings,
                a.keywords = $package.keywords,
                a.repository_type = $package.repository.type,
                a.repository_url = $package.repository.url,
                a.peerDependencies = $package.peerDependencies,
                a.dist_integrity = $package.dist.integrity,
                a.dist_shasum = $package.dist.shasum,
                a.dist_tarball = $package.dist.tarball,
                a.maintainers = $package.maintainers,
                a.contributors = $package.contributors


            RETURN a
            """,
            package=package.model_dump(),  # Use model_dump to convert the Pydantic object to a dictionary
        )
        # if not query_result:
        #     print("No results returned.")
        # else:
        #     print("Result:", query_result)
        #     for record in query_result:
        #         node = record["a"]
        #         print(node)
        # print(query_result)
        records = list(query_result)
        print(records)
        return query_result

    x = db.execute_write(_merge_package_tx)
    return x


def db_merge_package_full3j(package: PackageVersion):
    print("Adding package version to DB")
    print(f"package={package}")

    # Function to execute the Cypher query to merge the package into the database
    def _merge_package_tx(tx):
        query_result: Result = tx.run(
            """
            MERGE (a:PackageVersion
                {
                    package_id: $package.id
                })
            ON CREATE SET
                a.created = timestamp()
            ON MATCH SET
                a.counter = coalesce(a.counter, 0) + 1,
                a.accessTime = timestamp(),
                a.description = $package.description,
                a.latest_version = $package.version,
                a.created = COALESCE(a.created, timestamp()),
                a.from_package = $package.from_package,
                a.package_id = $package.id,
                a.nodeVersion = $package._nodeVersion,
                a.npm_operational_internal_host = $package.npm_operational_internal.host,
                a.npm_operational_internal_tmp = $package.npm_operational_internal.tmp,
                a.npm_user_email = $package._npmUser.email,
                a.npm_user_name = $package._npmUser.name,
                a.npm_version = $package._npmVersion,
                a.resolved = $package._resolved,
                a.shasum = $package._shasum,
                a.bin_ng_xi18n = $package.bin.ng_xi18n,
                a.bin_ngc = $package.bin.ngc,
                a.bugs_url = $package.bugs.url,
                a.description = $package.description,
                a.homepage = $package.homepage,
                a.license = $package.license,
                a.main = $package.main,
                a.typings = $package.typings,
                a.keywords = $package.keywords,
                a.repository_type = $package.repository.type,
                a.repository_url = $package.repository.url,
                a.peerDependencies = $package.peerDependencies,
                a.dist_integrity = $package.dist.integrity,
                a.dist_shasum = $package.dist.shasum,
                a.dist_tarball = $package.dist.tarball,
                a.maintainers = $package.maintainers,
                a.contributors = $package.contributors

                RETURN a
            """,
            package=package.model_dump(),  # Use model_dump to convert the Pydantic object to a dictionary
        )
        # if not query_result:
        #     print("No results returned.")
        # else:
        #     print("Result:", query_result)
        #     for record in query_result:
        #         node = record["a"]
        #         print(node)
        # print(query_result)
        records = list(query_result)
        print("--------------------records----------------------------")
        print(records)
        return query_result

    x = db.execute_write(_merge_package_tx)
    return x


def db_merge_package_full2(package: PackageVersion):
    print("Adding package version to DB")
    print(f"package={package}")

    # Function to execute the Cypher query to merge the package into the database
    def _merge_package_tx(tx):
        query_result: Result = tx.run(
            """
            MATCH (a:PackageVersion
                {
                    package_id: $package.id
                })
            UNWIND $package.relationships.dependencies as dependency
            MERGE (b:PackageVersion {package_id: dependency})
            MERGE (a)-[d:has_dependency]->(b)
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
                d.accessTime = timestamp(),
                a.description = $package.description,
                a.latest_version = $package.version,
                a.created = COALESCE(a.created, timestamp()),
                a.from_package = $package.from_package,
                a.package_id = $package.id,
                a.nodeVersion = $package._nodeVersion,
                a.npm_operational_internal_host = $package.npm_operational_internal.host,
                a.npm_operational_internal_tmp = $package.npm_operational_internal.tmp,
                a.npm_user_email = $package._npmUser.email,
                a.npm_user_name = $package._npmUser.name,
                a.npm_version = $package._npmVersion,
                a.resolved = $package._resolved,
                a.shasum = $package._shasum,
                a.bin_ng_xi18n = $package.bin.ng_xi18n,
                a.bin_ngc = $package.bin.ngc,
                a.bugs_url = $package.bugs.url,
                a.description = $package.description,
                a.homepage = $package.homepage,
                a.license = $package.license,
                a.main = $package.main,
                a.typings = $package.typings,
                a.keywords = $package.keywords,
                a.repository_type = $package.repository.type,
                a.repository_url = $package.repository.url,
                a.peerDependencies = $package.peerDependencies,
                a.dist_integrity = $package.dist.integrity,
                a.dist_shasum = $package.dist.shasum,
                a.dist_tarball = $package.dist.tarball,
                a.maintainers = $package.maintainers,
                a.contributors = $package.contributors

            RETURN d,a,b
            """,
            package=package.model_dump(),  # Use model_dump to convert the Pydantic object to a dictionary
        )
        # if not query_result:
        #     print("No results returned.")
        # else:
        #     print("Result:", query_result)
        #     for record in query_result:
        #         node = record["a"]
        #         print(node)
        # print(query_result)
        records = list(query_result)
        print(records)
        return query_result

    x = db.execute_write(_merge_package_tx)
    return x


#
# """
# MATCH (a:Package {package_id: $package.id})
# MERGE (a)-[:HAS_VERSION]->(v:PackageVersion {version: $package.version})
#
# SET
#     a.description = $package.description,
#     a.latest_version = $package.version,
#     a.created = COALESCE(a.created, timestamp()),
#
#     v.from_package = $package.from_package,
#     v.id = $package.id,
#     v.nodeVersion = $package._nodeVersion,
#     v.npm_operational_internal_host = $package.npm_operational_internal.host,
#     v.npm_operational_internal_host = $package.npm_operational_internal.tmp,
#     v.npm_user_email = $package._npmUser.email,
#     v.npm_user_name = $package._npmUser.name,
#     v.npm_version = $package._npmVersion,
#     v.resolved = $package._resolved,
#     v.shasum = $package._shasum,
#     v.bin_ng_xi18n = $package.bin.ng_xi18n,
#     v.bin_ngc = $package.bin.ngc,
#     v.bugs_url = $package.bugs.url,
#     v.description = $package.description,
#     v.homepage = $package.homepage,
#     v.license = $package.license,
#     v.main = $package.main,
#     v.typings = $package.typings,
#
#     v.keywords = $package.keywords,
#     v.repository_type = $package.repository.type,
#     v.repository_url = $package.repository.url,
#
#     v.peerDependencies = $package.peerDependencies,
#
#     v.dist_integrity = $package.dist.integrity,
#     v.dist_shasum = $package.dist.shasum,
#     v.dist_tarball = $package.dist.tarball,
#
#     v.maintainers = $package.maintainers,
#
#     v.contributors = $package.contributors,
#
#     v.created = timestamp()
#
# UNWIND $package.dependencies AS dependency
# MERGE (b:Package {package_id: dependency.package})
# MERGE (a)-[d:DependsOn {version: dependency.version}]->(b)
# ON CREATE SET
#     d.created = timestamp()
# ON MATCH SET
#     d.accessTime = timestamp()
#
# RETURN a, v, b, d
# """,

# def db_merge_package_full(package: PackageVersion):
#     print("Adding package to DB")
#     prettyPrint(package)
#
#     def _merge_package_tx(tx):
#         return tx.run(
#             """
#             MATCH (a:Package
#                 {
#                     package_id: $package.id,
#                     description: $package.description,
#                     latest_version: $package.latest_version
#
#                 })
#             UNWIND $package.dependencies as dependency
#             MERGE (b:Package {package_id: dependency.package})
#             MERGE (a)-[d:DependsOn {version: dependency.version}]->(b)
#             ON CREATE SET
#                 a.created = timestamp(),
#                 b.created = timestamp(),
#                 d.created = timestamp()
#             ON MATCH SET
#                 a.counter = coalesce(a.counter, 0) + 1,
#                 a.accessTime = timestamp(),
#
#                 b.counter = coalesce(a.counter, 0) + 1,
#                 b.accessTime = timestamp(),
#
#                 d.counter = coalesce(a.counter, 0) + 1,
#                 d.accessTime = timestamp()
#             RETURN d,a,b
#             """,
#             package=package.model_dump(),  # convert to dictionary
#         )
#
#     x = db.execute_write(_merge_package_tx)
#     # print(x)
#     return x
