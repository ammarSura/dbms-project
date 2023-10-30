from db_utils import run_query, set_missing_params_to_none


def post_booking_query(cur, args_dic, logger):
    try:
        cur.execute("""
            INSERT INTO bookings (listing_id, booker_id, start_date, end_date, cost, num_guests)
            VALUES (%(listing_id)s, %(booker_id)s, %(start_date)s, %(end_date)s, %(cost)s, %(num_guests)s)
            RETURNING id
        """, args_dic)
        result = cur.fetchone()
        cur.close()
        return result['id']
    except Exception as e:
        logger.error(e)
        return None

def post_booking(pool, args_dic, logger):
    set_missing_params_to_none(args_dic, [
        'listing_id',
        'user_id',
        'start_date',
        'end_date',
        'cost',
        'num_guests'
    ])
    return run_query(pool, lambda cur: post_booking_query(cur, args_dic, logger))
