from psycopg import Connection, Cursor, sql

from db_utils import run_query, select_query

def get_best_hosts(pool: Connection, args_dic: dict) -> int or None:
    fields = [
        sql.Identifier('best_hosts','id'),
        sql.Identifier('best_hosts', 'picture_url'),
        sql.Identifier('best_hosts', 'name'),
        sql.Identifier('best_hosts', 'avg_rating'),
        sql.Identifier('best_hosts', 'neighbourhood'),
        sql.Identifier('best_hosts', 'top_listings_id'),
        sql.Identifier('best_hosts', 'max_rating'),
    ]
    count = None
    extra_query = None
    if('count' in args_dic):
        count = args_dic['count']
        del args_dic['count']
    if('extra_query' in args_dic):
        extra_query = args_dic['extra_query']
        del args_dic['extra_query']

    return run_query(pool, lambda cur: select_query(cur, fields, 'best_hosts', args_dic, extra_query, count))
