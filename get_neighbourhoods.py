from psycopg import Connection
from db_utils import run_query, select_query

def get_neighbhourhoods_query(cur: Connection) -> int or None:
    return cur.execute(
        """
        SELECT DISTINCT neighborhood FROM listing;
        ORDER BY neighborhood;
        """
    ).fetchall()
def get_neighbourhoods(pool: Connection) -> int or None:
    return run_query(pool, lambda cur: get_neighbhourhoods_query(cur))
