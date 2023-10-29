from psycopg import Connection, Cursor
from db_utils import run_query, select_query, set_missing_params_to_none
from psycopg import sql

def get_listing(pool: Connection, args_dic: dict) -> int or None:
    count = None
    if('count' in args_dic):
        count = args_dic['count']
        del args_dic['count']
    return run_query(pool, lambda cur: select_query(cur, 'listing', args_dic, count))
