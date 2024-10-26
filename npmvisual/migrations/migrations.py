import time

from neo4j._sync.work.transaction import ManagedTransaction

from npmvisual import db
from npmvisual.migrations import bp
from npmvisual.utils2 import ns_hash


@bp.route("/test", methods=["GET"])
def create_first_db_timestamp():
    description = "created first db migration"
    # query = create_timestamp_query(message)

    # r = db.run(query)
    r = db.execute_write(create_migration_timestamp, description)
    print(r)
    return "success"


def create_migration_timestamp(
    tx: ManagedTransaction,
    description,
):
    timestamp = time.time()
    hash = ns_hash(description + str(timestamp), 24)
    id = f"${timestamp}_${hash}_${description[24]}"

    result = tx.run(
        """
        MERGE (m:Migration{
            migration_id: $id,
            description: $description,
            timestamp: $timestamp
          })
        ON CREATE SET m.created = timestamp()
        ON MATCH SET
        m.counter = coalesce(m.counter, 0) + 1,
        m.accessTime = timestamp()
        RETURN m
        """,
        id=id,
        description=description,
        timestamp=timestamp,
    )
    return result
    # q = " \
    #     "CREATE (%s:MigrationTimestamp " \
    #     "{timestamp: '${timestamp}', message:'${message}'})"
    # return q


def set_db_timestamp():
    pass
