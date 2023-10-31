from psycopg import sql

from db_utils import run_query, select_query


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
    count = None
    extra_query = None
    page = None
    extra_fields = []
    if ('count' in args_dic):
        count = args_dic['count']
        del args_dic['count']
    if ('page' in args_dic):
        page = args_dic['page']
        del args_dic['page']
    if ('extra_query' in args_dic):
        extra_query = args_dic['extra_query']
        del args_dic['extra_query']
    if ('extra_fields' in args_dic):
        extra_fields = args_dic['extra_fields']
        del args_dic['extra_fields']
    fields = [
        sql.Identifier('bookings', 'id'),
        sql.Identifier('bookings', 'listing_id'),
        sql.Identifier('bookings', 'booker_id'),
        sql.Identifier('bookings', 'start_date'),
        sql.Identifier('bookings', 'end_date'),
        sql.Identifier('bookings', 'cost'),
        sql.Identifier('bookings', 'num_guests'),
        sql.Identifier('bookings', 'created_at'),
        sql.Identifier('bookings', 'updated_at'),
        sql.Identifier('bookings', 'status')
    ]
    fields.extend(extra_fields)

    return run_query(pool, lambda cur: select_query(cur, fields, 'bookings', args_dic, extra_query, count, page))
