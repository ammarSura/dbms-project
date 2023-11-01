import time
from typing import Callable
from statistics import mean
from psycopg import ClientCursor, Cursor, sql
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from env import DB_URL

def set_missing_params_to_none(args_dic: dict, required_params: list):
    for param in required_params:
        if param not in args_dic:
            args_dic[param] = None


def run_query(pool: ConnectionPool, query: Callable[[], Cursor], q_id: str = None):
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            start_time = time.time()
            res = query(cur)
            end_time = time.time()
            if q_id:
                get_timings('{},{}'.format(q_id, (end_time - start_time) * 1000))
            return res


def create_pool():
    pool = ConnectionPool(
        conninfo=DB_URL,
    )
    pool.wait()
    print('Pool created')
    return pool


def select_query(cur: Cursor, fields: list[sql.Identifier], table_name: str, args_dic: dict, extra_query: dict = None, count: int = None, page: int = None, order_by: str = None) -> dict or None:
    query_lst = [
        sql.SQL("SELECT {fields} FROM {table_name}")
        .format(
            fields=sql.SQL(', ').join(fields),
            table_name=sql.Identifier(table_name)
        )
    ]

    if (extra_query and 'query_lst' in extra_query and len(extra_query['query_lst']) > 0):
        query_lst.extend(extra_query['query_lst'])
    for param, value in args_dic.items():
        if (value):
            query_string = sql.Composed(query_lst).as_string(cur)
            if (len(query_lst) == 1 or 'WHERE' not in query_string) :
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

    if(order_by):
        query_lst.append(
            sql.SQL("\nORDER BY {order_by}").format(
                order_by=sql.Identifier(order_by)
            )
        )
    if (count):
        query_lst.append(
            sql.SQL("\nLIMIT %(count)s")
        )
    args_dic['count'] = count or 10

    if (page):
        query_lst.append(
            sql.SQL("\nOFFSET %(offset)s")
        )
        args_dic['offset'] = page * args_dic['count']

    extra_query and 'args_dic' in extra_query and args_dic.update(
        extra_query['args_dic'])
    query = sql.Composed(query_lst)
    try:
        start_time = time.time()
        cur.execute(
            query,
            args_dic
        )
        end_time = time.time()
        log_query(cur, query, args_dic, table_name, 'select', end_time - start_time)
        if (count):
            result = cur.fetchall()
        else:
            result = cur.fetchone()
        return result
    except Exception as e:
        cur1 = ClientCursor(cur.connection)
        print('query failed', cur1.mogrify(query, args_dic))



def query_append_check(query_lst: list):
    if (len(query_lst) > 1):
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

def update_query(cur, args_dic, id, table_name):
    try:
        update_lst = [
            sql.SQL('UPDATE {table_name}').format(
                table_name=sql.Identifier(table_name)
            )
        ]
        for key in args_dic:
            if args_dic[key]:
                if(len(update_lst) < 2):
                    update_lst.append(sql.SQL('\nSET '))

                update_lst.append(sql.SQL('{} = {},').format(
                    sql.Identifier(key),
                    sql.Literal(args_dic[key])
                ))
        if(len(update_lst) < 2):
                return None
        update_lst.append(sql.SQL('updated_at = NOW()'))
        update_lst.append(sql.SQL('\nWHERE id = %(id)s'))
        update_lst.append(sql.SQL('\nRETURNING id'))
        args_dic['id'] = id
        query =sql.Composed(update_lst)
        start_time = time.time()
        cur.execute(
            query,
            args_dic
        )
        end_time = time.time()
        result = cur.fetchone()
        log_query(cur, query, args_dic, table_name, 'update', (end_time - start_time))
        cur.close()
        return result['id']
    except Exception as e:
        return None

def post_query(cur, table_name, args_dic):
    query = sql.SQL("""INSERT INTO {table}({cols}) VALUES ({values})RETURNING id;"""
    ).format(
            table=sql.Identifier(table_name),
            cols=sql.SQL(", ").join(map(sql.Identifier, args_dic.keys())),
            values=sql.SQL(",").join(map(sql.Placeholder, args_dic.keys()))
        )
    try:
        start_time = time.time()
        cur.execute(query, args_dic)
        end_time = time.time()
        log_query(cur, query, args_dic, table_name, 'post', end_time - start_time)
        return cur.fetchone()['id']
    except Exception as e:
        cur1 = ClientCursor(cur.connection)
        print('Error: ', e, args_dic)
        return None
def get_timings(id: str):
    with open("test.txt", "a") as myfile:
        myfile.write(id + '\n')


def log_query(cur: Cursor, query: str, args_dic: dict, table_name: str, op: str, run_time: float):
    cur1 = ClientCursor(cur.connection)
    query = cur1.mogrify(query, args_dic)
    x = str(op + ' ' + table_name + '||' + str(run_time) + '||' + query + '\n=========================\n')
    with open("queries.csv", "a") as myfile:
        myfile.write(x)

def process_timings():
    with open("test.txt", "r") as myfile:
        data = myfile.readlines()
        timings = {}
        for datum in data:
            datum = datum.strip()
            datum = datum.split(',')
            timing = float(datum[1])
            id = datum[0]
            if id not in timings:
                timings[id] = []
            timings[id].append(timing)
    timing_lst = []
    for id in timings:
        timings[id].sort(reverse=True)
        timing_lst.append({
            'id': id,
            'mean': mean(timings[id]),
            'max': max(timings[id]),
            'timings': timings[id]
        })
    timing_lst.sort(key=lambda x: x['mean'], reverse=True)
    with open("processed_timings.txt", "w") as myfile:
        myfile.write('id,mean,max,timings\n')
        for timing in timing_lst:
            myfile.write(timing['id'] + ',' + str(timing['mean']) + ',' + str(timing['max']) + ',' + str(timing['timings']) + '\n')

if __name__ == "__main__":
    cleaned_queries = []
    with open("queries.csv", "r") as myfile:
        lines = myfile.read().split('\n=========================\n')
        for datum in lines:
            if(len(datum) < 1):
                continue
            op, run_time, query = datum.split('||')
            query = query.strip()
            query = ' '.join(query.split('\n'))
            cleaned_queries.append({
                'op': op,
                'run_time': str(float(run_time) * 1000),
                'query': query
            })
    with open("queries_cleaned.csv", "w") as myfile:
        myfile.write('op,run_time,query\n')
        for datum in cleaned_queries:
            myfile.write(datum['op'] + '|' + datum['run_time'] + '|' + datum['query'] + '\n')

