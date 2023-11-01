from psycopg import Connection, Cursor, sql
from utils.db_utils import run_query, select_query, set_missing_params_to_none


def get_reviews(pool, args_dic):
    fields = [
        sql.Identifier('reviews', 'id'),
        sql.Identifier('reviews', 'listing_id'),
        sql.Identifier('reviews', 'reviewer_id'),
        sql.Identifier('reviews', 'comments'),
        sql.Identifier('reviews', 'rating'),
        sql.Identifier('reviews', 'created_at'),
        sql.Identifier('users', 'name'),
        sql.Identifier('users', 'picture_url'),
    ]
    count = None
    extra_query = {
        'query_lst': [
            sql.SQL('\nJOIN users ON reviews.reviewer_id = users.id'),
        ]
    }
    if ('count' in args_dic):
        count = args_dic['count']
        del args_dic['count']

    if ('id' in args_dic):
        id = args_dic['id']
        del args_dic['id']
        args_dic['reviews.id'] = id
    return run_query(pool, lambda cur: select_query(cur, fields, 'reviews', args_dic, extra_query, count, None, 'created_at'))
