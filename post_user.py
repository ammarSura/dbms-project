from logging import Logger

from psycopg import Connection, Cursor

from db_utils import run_query, set_missing_params_to_none


def post_user_query(cur: Cursor, args_dic: dict, logger: Logger) -> int or None:
    try:
        cur.execute("""
            INSERT INTO users (name, picture_url, email, password)
            VALUES (%(name)s, %(picture_url)s, %(email)s, %(password)s)
            RETURNING id
        """, args_dic)
        result = cur.fetchone()
        return result['id']
    except Exception as e:
        logger.error(e)
        return None


def post_user(pool: Connection, args_dic: dict, logger: Logger) -> int or None:
    set_missing_params_to_none(
        args_dic, ['name', 'picture_url', 'email', 'password'])
    posted_host_id = run_query(
        pool, lambda cur: post_user_query(cur, args_dic, logger))
    return posted_host_id
