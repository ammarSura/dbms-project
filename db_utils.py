import sys
from psycopg import ClientCursor, Cursor, sql
from psycopg_pool import ConnectionPool
from typing import Callable
from env import DB_URL
from psycopg.rows import dict_row

def set_missing_params_to_none(args_dic: dict, required_params: list):
    for param in required_params:
        if param not in args_dic:
            args_dic[param] = None

def run_query(pool: ConnectionPool, query: Callable[[], Cursor]):
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            return query(cur)


def create_pool():
    pool = ConnectionPool(
        conninfo=DB_URL
    )
    pool.wait()
    print('Pool created')
    return pool

def select_query(cur: Cursor, fields: list[sql.Identifier], table_name: str, args_dic: dict, extra_query: dict = None, count: int = None, page: int = None) -> dict or None:
    query_lst = [
        sql.SQL("SELECT {fields} FROM {table_name}")
            .format(
                fields=sql.SQL(', ').join(fields),
                table_name=sql.Identifier(table_name)
            )
    ]

    if(extra_query and 'query_lst' in extra_query and len(extra_query['query_lst']) > 0):
        query_lst.extend(extra_query['query_lst'])
    for param, value in args_dic.items():
        if(value):
            if(len(query_lst) == 1):
                query_lst.append(
                    sql.SQL(
                        "\nWHERE {pkey} = %({pkey})s".format(
                            pkey=param,
                        ))
                )
            else:
                query_lst.append(
                    sql.SQL(
                        "\nAND {pkey} = %({pkey})s".format(
                            pkey=param,
                        ))
                )
    if(count):
        query_lst.append(
            sql.SQL("\nLIMIT %(count)s")
        )
    args_dic['count'] = count or 10

    if(page):
        query_lst.append(
            sql.SQL("\nOFFSET %(offset)s")
        )
        args_dic['offset'] = page * args_dic['count']

    extra_query and 'args_dic' in extra_query and args_dic.update(extra_query['args_dic'])
    query = sql.Composed(query_lst)
    cursor = ClientCursor(create_pool().getconn())
    print('mogrify', cursor.mogrify(query, args_dic), file=sys.stdout)

    cur.execute(
        query,
        args_dic
    )

    result = None
    if(count):
        result = cur.fetchall()
    else:
        result = cur.fetchone()
    return result

def query_append_check(query_lst: list):
    if(len(query_lst) > 1):
        query_lst.append(
                sql.SQL(
                    "\nAND "
                )
            )
    else:
            query_lst.append(
            sql.SQL(
                "\nWHERE ")
        )
