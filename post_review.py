from logging import Logger
from utils.db_utils import post_query, run_query, set_missing_params_to_none
from psycopg_pool import ConnectionPool


def post_review_query(cur, args_dic, logger):
    try:
        cur.execute("""
            INSERT INTO reviews (listing_id, reviewer_id, comments, rating)
            VALUES (%(listing_id)s, %(reviewer_id)s, %(comments)s, %(rating)s)
            RETURNING id
        """, args_dic)
        result = cur.fetchone()
        return result['id']
    except Exception as e:
        logger.error(e)
        return None


def post_review(pool: ConnectionPool, args_dic: dict, logger: Logger) -> int or None:
    posted_review_id = run_query(
        pool, lambda cur: post_query(cur, 'reviews', args_dic))
    return posted_review_id
