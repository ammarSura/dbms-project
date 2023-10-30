from psycopg import Connection
from psycopg_pool import ConnectionPool

from db_utils import run_query


def get_neighbhourhoods_query(cur: Connection) -> int or None:
    return cur.execute(
        """
        SELECT DISTINCT neighborhood FROM listing
        ORDER BY neighborhood;
        """
    ).fetchall()


def get_neighbourhoods(pool: ConnectionPool) -> int or None:
    return run_query(pool, lambda cur: get_neighbhourhoods_query(cur))
