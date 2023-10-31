import sys
from logging import Logger

from psycopg import Connection, Cursor

from db_utils import run_query, set_missing_params_to_none


def get_user_query(cur: Cursor, args_dic: dict) -> dict or None:
    cur.execute("""
        SELECT password, name, is_host, picture_url, email, created_at, updated_at, id FROM users
        WHERE id = %s
    """, [args_dic['id']])
    result = cur.fetchone()
    return result


def get_user(pool: Connection, args_dic: dict) -> dict or None:
    set_missing_params_to_none(args_dic, [
        'id',
    ])
    user = run_query(pool, lambda cur: get_user_query(cur, args_dic))
    return user
