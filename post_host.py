from logging import Logger

from psycopg import Cursor
from psycopg_pool import ConnectionPool

from utils.db_utils import post_query, run_query, set_missing_params_to_none


def post_host_query(cur: Cursor, args_dic: dict, logger: Logger) -> int or None:
    try:
        cur.execute(
            """
            INSERT INTO hosts (about, response_time, response_rate, acceptance_rate, is_superhost, identity_verified, user_id, neighbourhood, location)
            VALUES (%(about)s, %(response_time)s, %(response_rate)s, %(acceptance_rate)s, %(is_superhost)s, %(identity_verified)s, %(user_id)s, %(neighbourhood)s, %(location)s)
            RETURNING id
        """, args_dic)
        result = cur.fetchone()
        return result['id']
    except Exception as e:
        logger.error('Post hosts error: %s', e)
        logger.error('Post hosts args: %s', args_dic)
        return None


def post_host(pool: ConnectionPool, args_dic: dict, logger: Logger) -> int or None:

    posted_host_id = run_query(
        pool, lambda cur: post_query(cur, 'hosts', args_dic))
    return posted_host_id
