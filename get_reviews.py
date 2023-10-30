from psycopg import Connection, Cursor,sql
from db_utils import run_query, select_query, set_missing_params_to_none

def get_review_query(cur: Cursor, args_dic: dict):
    cur.execute(
        """
            SELECT * FROM reviews
            WHERE id = %(id)s
        """,
        args_dic
    )
    result = cur.fetchone()
    return result
def get_reviews(pool, args_dic):
    fields = [
        sql.Identifier('reviews','id'),
        sql.Identifier('reviews','listing_id'),
        sql.Identifier('reviews','reviewer_id'),
        sql.Identifier('reviews','comments'),
        sql.Identifier('reviews','rating'),
        sql.Identifier('reviews', 'created_at'),
    ]
    return run_query(pool, lambda cur: select_query(cur, fields, 'reviews', args_dic))
