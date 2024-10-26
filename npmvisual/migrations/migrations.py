from npmvisual import db
from npmvisual.utils2 import ns_hash

import time
from neo4j._sync.work.transaction import ManagedTransaction

"""
DO NOT EVER EDIT FUNCTIONS IN THIS FILE. I HAVE NOT MADE DOWNGRADE. 
JUST ADD MORE UPGRADES TO FIX STUFF

COPY PASTE IS YOUR FRIEND. 

name of migrations should be: "migration_timestamp"
where timestamp is milliseconds since the epoch. 

I made a handy CopyTimestamp.tsx component on the website. use that. 
"""


def migration_1729922231172():
    """created new db migration system"""

    def create_migration_system(
        tx: ManagedTransaction,
        migration_id: str,
    ):
        tx.run(
            """
            MERGE (m:Migration {
                migration_id: $migration_id
            })
            ON CREATE SET m.created = timestamp()
            ON MATCH SET
            m.counter = coalesce(m.counter, 0) + 1,
            m.accessTime = timestamp()
            """,
            migration_id=migration_id,
        )

    db.execute_write(create_migration_system, "migration_1729922231172")


#
#
# def migration_1729922231172():
#     """created new db migration system"""
#     db.execute_write(create_migration_timestamp_002, "migration_1729921513660")
#
#
# def migration_1729919486297():
#     description = "created first db migration"
#     db.execute_write(create_migration_timestamp_001, description)
#
#
# def create_migration_timestamp_002(
#     tx: ManagedTransaction,
#     migration_id: str,
# ):
#     tx.run(
#         """
#         MERGE (m:Migration {
#             migration_id: $migration_id
#           })
#         ON CREATE SET m.created = timestamp()
#         ON MATCH SET
#         m.counter = coalesce(m.counter, 0) + 1,
#         m.accessTime = timestamp()
#         """,
#         migration_id=migration_id,
#     )
#
#
# def create_migration_timestamp_001(
#     tx: ManagedTransaction,
#     description,
# ):
#     timestamp = time.time()
#     hash = ns_hash(description + str(timestamp), 24)
#     id = f"${timestamp}_${hash}_${description[:24]}"
#
#     tx.run(
#         """
#         MERGE (m:Migration{
#             migration_id: $id,
#             description: $description,
#             timestamp: $timestamp
#           })
#         ON CREATE SET m.created = timestamp()
#         ON MATCH SET
#         m.counter = coalesce(m.counter, 0) + 1,
#         m.accessTime = timestamp()
#         RETURN m
#         """,
#         id=id,
#         description=description,
#         timestamp=timestamp,
#     )
