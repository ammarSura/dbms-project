from psycopg import Connection, Cursor, sql

from db_utils import run_query, select_query, set_missing_params_to_none


def get_listing(pool: Connection, args_dic: dict) -> int or None:
    count = None
    extra_query = None
    page = None
    if ('count' in args_dic):
        count = args_dic['count']
        del args_dic['count']
    if ('page' in args_dic):
        page = args_dic['page']
        del args_dic['page']
    if ('extra_query' in args_dic):
        extra_query = args_dic['extra_query']
        del args_dic['extra_query']
    fields = [
        sql.Identifier('listing', 'id'),
        sql.Identifier('listing', 'picture_url'),
        sql.Identifier('listing', 'name'),
        sql.Identifier('listing', 'price'),
        sql.Identifier('listing', 'room_type'),
        sql.Identifier('listing', 'review_rating'),
    ]
    return run_query(pool, lambda cur: select_query(cur, fields, 'listing', args_dic, extra_query, count, page))
