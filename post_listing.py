from logging import Logger

from psycopg import Connection, Cursor

from db_utils import post_query, run_query, set_missing_params_to_none


def post_listing_query(cur: Cursor, args_dic: dict, logger: Logger) -> int or None:
    try:
        cur.execute(
            """
            INSERT INTO listings (name, picture_url, coord, price, property_type, room_type, accommodates, bathrooms, bedrooms, beds, amenities, host_id, neighbourhood, neighbourhood_overview, rating, location)
            VALUES (%(name)s, %(picture_url)s, %(coord)s, %(price)s, %(property_type)s, %(room_type)s, %(accommodates)s, %(bathrooms)s, %(bedrooms)s, %(beds)s, %(amenities)s, %(host_id)s, %(neighbourhood)s, %(neighbourhood_overview)s, %(rating)s, %(location)s)
            RETURNING id
        """, args_dic)
        result = cur.fetchone()
        return result['id']
    except Exception as e:
        logger.error('Post host error: %s', e)
        logger.error('Post host args: %s', args_dic)
        return None


def post_listing(pool: Connection, args_dic: dict, logger: Logger) -> int or None:
    posted_host_id = run_query(
        pool, lambda cur: post_query(cur, 'listings', args_dic))
    return posted_host_id
