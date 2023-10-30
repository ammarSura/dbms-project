from psycopg import Connection, Cursor, sql

from db_utils import run_query, select_query, set_missing_params_to_none


def get_best_listing(pool: Connection, args_dic: dict) -> int or None:
    extra_query = None
    if('extra_query' in args_dic):
        extra_query = args_dic['extra_query']
        del args_dic['extra_query']
    fields = [
        sql.Identifier('listing','id'),
        sql.Identifier('listing', 'picture_url'),
        sql.Identifier('listing', 'name'),
        sql.Identifier('listing', 'price'),
        sql.Identifier('listing', 'room_type'),
        sql.Identifier('listing', 'review_rating'),
    ]
    return run_query(pool, lambda cur: select_query(cur, fields, 'best_listings', args_dic, extra_query, count, page))
