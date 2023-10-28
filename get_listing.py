from psycopg import Connection, Cursor
from db_utils import run_query, set_missing_params_to_none

def get_listing_query(cur: Cursor, args_dic: dict):
    cur.execute("""
        SELECT * FROM listing
        WHERE id = %(id)s
    """,
    args_dic
    )
    result = cur.fetchone()
    return result

def get_listing(pool: Connection, args_dic: dict) -> int or None:
    set_missing_params_to_none(args_dic, [
        'id',
    ])
    return run_query(pool, lambda cur: get_listing_query(cur, args_dic))
