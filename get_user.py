import sys
from logging import Logger

from psycopg import Connection, Cursor

from db_utils import run_query, set_missing_params_to_none


def get_user_query(cur: Cursor, args_dic: dict) -> dict or None:
    cur.execute("""
        SELECT * FROM users
        WHERE id = %(id)s
    """, args_dic)
    result = cur.fetchone()
    return result


def get_user(pool: Connection, args_dic: dict) -> dict or None:
    set_missing_params_to_none(args_dic, [
        'id',
    ])
    user = run_query(pool, lambda cur: get_user_query(cur, args_dic))
    return user
