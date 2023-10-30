from logging import Logger

from psycopg import Connection, Cursor

from db_utils import run_query, set_missing_params_to_none


def post_listing_query(cur: Cursor, args_dic: dict, logger: Logger) -> int or None:
    try:
        cur.execute(
            """
            INSERT INTO listing (name, picture_url, coors, price, property_type, room_type, accommodates, bathrooms, bedrooms, beds, bed_type, amenities, host_id, neighborhood, neighborhood_overview, review_rating)
            VALUES (%(name)s, %(picture_url)s, %(coors)s, %(price)s, %(property_type)s, %(room_type)s, %(accommodates)s, %(bathrooms)s, %(bedrooms)s, %(beds)s, %(bed_type)s, %(amenities)s, %(host_id)s, %(neighborhood)s, %(neighborhood_overview)s, %(review_rating)s)
            RETURNING id
        """, args_dic)
        result = cur.fetchone()
        return result['id']
    except Exception as e:
        logger.error('Post host error: %s', e)
        logger.error('Post host args: %s', args_dic)
        return None


def post_listing(pool: Connection, args_dic: dict, logger: Logger) -> int or None:
    params = [
        'name',
        'picture_url',
        'coors',
        'price',
        'property_type',
        'room_type',
        'accommodates',
        'bathrooms',
        'bedrooms',
        'beds',
        'bed_type',
        'amenities',
        'host_id',
        'neighborhood',
        'neighborhood_overview',
        'review_rating',
    ]
    set_missing_params_to_none(args_dic, params)
    posted_host_id = run_query(
        pool, lambda cur: post_listing_query(cur, args_dic, logger))
    return posted_host_id
