from psycopg import Connection, Cursor, sql
from db_utils import run_query, select_query, set_missing_params_to_none



def get_host(pool: Connection, args_dic: dict):

    fields = [
        sql.Identifier('id'),
        sql.Identifier('user_id'),
        sql.Identifier('location'),
        sql.Identifier('neighbourhood'),
        sql.Identifier('about'),
        sql.Identifier('response_time'),
        sql.Identifier('response_rate'),
        sql.Identifier('acceptance_rate'),
        sql.Identifier('is_superhost'),
        sql.Identifier('identity_verified'),
        sql.Identifier('host_since'),
        sql.Identifier('updated_at'),
    ]
    return run_query(pool, lambda cur: select_query(cur, fields, 'hosts', args_dic))
