from psycopg import Connection, Cursor, sql

from utils.db_utils import run_query, select_query, set_missing_params_to_none


def get_listing(pool: Connection, args_dic: dict):
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

    if ('id' in args_dic):
        id = args_dic['id']
        del args_dic['id']
        args_dic['listings.id'] = id
    fields = [
        sql.Identifier('listings', 'id'),
        sql.Identifier('listings', 'picture_url'),
        sql.Identifier('listings', 'name'),
        sql.Identifier('listings', 'price'),
        sql.Identifier('listings', 'room_type'),
        sql.Identifier('listings', 'rating'),
        sql.Identifier('listings', 'host_id'),
        sql.Identifier('listings', 'neighbourhood'),
        sql.Identifier('listings', 'neighbourhood_overview'),
        sql.Identifier('listings', 'location'),
        sql.Identifier('listings', 'description'),
        sql.Identifier('listings', 'property_type'),
        sql.Identifier('listings', 'accommodates'),
        sql.Identifier('listings', 'bathrooms'),
        sql.Identifier('listings', 'bedrooms'),
        sql.Identifier('listings', 'beds'),
        sql.Identifier('listings', 'amenities'),
        sql.Identifier('listings', 'created_at'),
        sql.Identifier('listings', 'updated_at'),
        sql.Identifier('listings', 'min_nights'),
        sql.Identifier('listings', 'max_nights'),
    ]

    fields.extend(extra_fields)
    return run_query(pool, lambda cur: select_query(cur, fields, 'listings', args_dic, extra_query, count, page))
