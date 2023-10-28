from psycopg import Cursor
from psycopg_pool import ConnectionPool
from typing import Callable
from env import DB_URL
from psycopg.rows import dict_row

def set_missing_params_to_none(args_dic: dict, required_params: list):
    for param in required_params:
        if param not in args_dic:
            args_dic[param] = None

def run_query(pool: ConnectionPool, query: Callable[[], Cursor]):
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            return query(cur)


def create_pool():
    pool = ConnectionPool(
        conninfo=DB_URL
    )
    pool.wait()
    print('Pool created')
    return pool

