from psycopg import Connection, Cursor, sql

from db_utils import run_query, select_query, set_missing_params_to_none


def get_best_listing(pool: Connection, args_dic: dict) -> int or None:
    extra_query = None
    if('extra_query' in args_dic):
        extra_query = args_dic['extra_query']
        del args_dic['extra_query']
    fields = [
        sql.Identifier('best_listings','id'),
        sql.Identifier('best_listings', 'picture_url'),
        sql.Identifier('best_listings', 'name'),
        sql.Identifier('best_listings', 'price'),
        sql.Identifier('best_listings', 'room_type'),
        sql.Identifier('best_listings', 'rating'),
    ]
    return run_query(pool, lambda cur: select_query(cur, fields, 'best_listings', args_dic, extra_query, count, page))
