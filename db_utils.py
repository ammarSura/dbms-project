from psycopg import Cursor, sql, ClientCursor
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

def select_query(cur: Cursor, table_name: str, args_dic: dict, count: int = None) -> dict or None:
    query_lst = [
        sql.SQL("SELECT * FROM {table_name}").format(
            table_name=sql.Identifier(table_name)
        )
    ]
    for param, value in args_dic.items():
        if(value):
            query_lst.append(
                sql.SQL(
                    "\nWHERE {pkey} = %({pkey})s".format(
                        pkey=param,
                    ))
            )
    if(count):
        query_lst.append(
            sql.SQL("\nLIMIT %(count)s")
        )
    query = sql.Composed(query_lst)
    args_dic['count'] = count or 10
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
