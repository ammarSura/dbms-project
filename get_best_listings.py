from psycopg import Connection, Cursor, sql

from utils.db_utils import run_query, select_query, set_missing_params_to_none


def get_best_listing(pool: Connection, args_dic: dict) -> int or None:
    fields = [
        sql.Identifier('best_listings', 'id'),
        sql.Identifier('best_listings', 'picture_url'),
        sql.Identifier('best_listings', 'name'),
        sql.Identifier('best_listings', 'price'),
        sql.Identifier('best_listings', 'room_type'),
        sql.Identifier('best_listings', 'rating'),
        sql.Identifier('best_listings', 'reviewer_name'),
        sql.Identifier('best_listings', 'comments'),
        sql.Identifier('best_listings', 'neighbourhood'),
    ]
    count = None
    extra_query = None
    order_by = None
    if ('extra_query' in args_dic):
        extra_query = args_dic['extra_query']
        del args_dic['extra_query']
    if ('count' in args_dic):
        count = args_dic['count']
        del args_dic['count']
    if ('is_budget' in args_dic):
        is_budget = args_dic['is_budget']
        del args_dic['is_budget']
        if (is_budget):
            if (extra_query is not None):
                Exception('Not implemented')
            extra_query = {
                'query_lst': [
                    sql.SQL('\nWHERE best_listings.price < 100'),
                ]
            }
            order_by = 'price'
    return run_query(pool, lambda cur: select_query(cur, fields, 'best_listings', args_dic, extra_query or None, count, None, order_by))
