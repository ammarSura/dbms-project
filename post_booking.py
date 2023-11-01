from utils.db_utils import post_query, run_query, set_missing_params_to_none
from psycopg import sql, ClientCursor


def post_booking(pool, args_dic, logger):
    return run_query(pool, lambda cur: post_query(cur, 'bookings', args_dic))
