import sys
from logging import Logger

from psycopg import Connection, Cursor, sql

from db_utils import run_query, select_query, set_missing_params_to_none


def get_user_query(cur: Cursor, args_dic: dict) -> dict or None:
    cur.execute("""
        SELECT password, name, is_host, picture_url, email, created_at, updated_at, id FROM users
        WHERE id = %s
    """, [args_dic['id']])
    result = cur.fetchone()
    return result


def get_user(pool: Connection, args_dic: dict) -> dict or None:
    fields = [
        sql.Identifier('users', 'id'),
        sql.Identifier('users', 'name'),
        sql.Identifier('users', 'picture_url'),
        sql.Identifier('users', 'email'),
        sql.Identifier('users', 'password'),
        sql.Identifier('users', 'is_host'),
        sql.Identifier('users', 'created_at'),
        sql.Identifier('users', 'updated_at'),
    ]
    user = run_query(pool, lambda cur: select_query(cur, fields, 'users', args_dic))
    return user
