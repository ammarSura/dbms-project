from psycopg import Cursor
from psycopg_pool import ConnectionPool
from typing import Callable
import logging
from env import DB_URL

def run_query(pool: ConnectionPool, query: Callable[[], Cursor]):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            return query(cur)

def create_pool():
    pool = ConnectionPool(
        conninfo=DB_URL
    )
    pool.wait()
    logging.info('DB initiated')
    return pool

