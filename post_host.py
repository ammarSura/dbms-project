from logging import Logger

from psycopg import Cursor
from psycopg_pool import ConnectionPool

from db_utils import run_query, set_missing_params_to_none


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
    set_missing_params_to_none(args_dic, [
        'user_id',
        'is_superhost',
        'about',
        'response_rate',
        'response_time',
        'identity_verified',
        'acceptance_rate',
    ])
    posted_host_id = run_query(
        pool, lambda cur: post_host_query(cur, args_dic, logger))
    return posted_host_id
