from logging import Logger

from psycopg import Cursor
from psycopg_pool import ConnectionPool

from utils.db_utils import post_query, run_query, set_missing_params_to_none


def post_user(pool: ConnectionPool, args_dic: dict, logger: Logger) -> int or None:

    posted_host_id = run_query(
        pool, lambda cur: post_query(cur, 'users', args_dic))
    return posted_host_id
