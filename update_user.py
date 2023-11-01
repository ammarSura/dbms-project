import sys
from utils.db_utils import create_pool, run_query, update_query
from psycopg import sql, ClientCursor


def update_user(pool, args_dic, id: str):
    return run_query(pool, lambda cur: update_query(cur, args_dic, id, 'users'))
