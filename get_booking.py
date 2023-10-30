from db_utils import run_query, select_query
from psycopg import sql

def get_bookings_query(cur, args_dic, logger):
    try:
        cur.execute("""
            SELECT * FROM bookings WHERE user_id = %(user_id)s
        """, args_dic)
        result = cur.fetchall()
        return result
    except Exception as e:
        logger.error(e)
        return None

def get_bookings(pool, args_dic):
    fields = [
        sql.Identifier('bookings','id'),
        sql.Identifier('bookings','listing_id'),
        sql.Identifier('bookings','booker_id'),
        sql.Identifier('bookings','start_date'),
        sql.Identifier('bookings','end_date'),
        sql.Identifier('bookings','cost'),
        sql.Identifier('bookings','num_guests'),
        sql.Identifier('bookings','created_at'),
    ]
    count = None
    if('count' in args_dic):
        count = args_dic['count']
        del args_dic['count']
    return run_query(pool, lambda cur: select_query(cur, fields, 'bookings', args_dic, None, count))
