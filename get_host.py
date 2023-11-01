from psycopg import Connection, Cursor, sql
from db_utils import run_query, select_query, set_missing_params_to_none



def get_host(pool: Connection, args_dic: dict):
    fields = [
        sql.Identifier('hosts', 'id'),
        sql.Identifier('hosts', 'user_id'),
        sql.Identifier('hosts', 'location'),
        sql.Identifier('hosts', 'neighbourhood'),
        sql.Identifier('hosts', 'about'),
        sql.Identifier('hosts', 'response_time'),
        sql.Identifier('hosts', 'response_rate'),
        sql.Identifier('hosts', 'acceptance_rate'),
        sql.Identifier('hosts', 'is_superhost'),
        sql.Identifier('hosts', 'identity_verified'),
        sql.Identifier('hosts', 'host_since'),
        sql.Identifier('hosts', 'updated_at'),
    ]
    extra_query = None

    if('id' in args_dic):
        id = args_dic['id']
        del args_dic['id']
        args_dic['hosts.id'] = id
    if('extra_fields' in args_dic):
        fields.extend(args_dic['extra_fields'])
        del args_dic['extra_fields']
    if('extra_query' in args_dic):
        extra_query = args_dic['extra_query']
        del args_dic['extra_query']
    return run_query(pool, lambda cur: select_query(cur, fields, 'hosts', args_dic, extra_query))
