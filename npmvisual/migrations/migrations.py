import time

from npmvisual import db
from npmvisual.migrations import bp
from npmvisual.utils2 import ns_hash


@bp.route("/test", methods=["GET"])
def create_first_db_timestamp():
    message = "created first db migration"
    # query = create_timestamp_query(message)

    # r = db.run(query)
    name = message
    r = db.execute_write(create_timestamp_query, name)
    print(r)
    return "success"


def create_timestamp_query(tx, name):
    timestamp = time.time()
    result = tx.run(
        """
        MERGE (p:Person {name: $name})
        RETURN p.name AS nameP
        """,
        name=name,
    )
    return result
    # timestamp = time.time()
    # hash = ns_hash(message + str(timestamp))
    # name = f"${timestamp}_${hash}_${message}"
    # q = " \
    #     "CREATE (%s:MigrationTimestamp " \
    #     "{timestamp: '${timestamp}', message:'${message}'})"
    # return q


def set_db_timestamp():
    pass
