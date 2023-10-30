import sys
from db_utils import create_pool, run_query
from psycopg import sql, ClientCursor

def update_user_query(cur, args_dic, id):
    try:
        update_lst = [
            sql.SQL('UPDATE users')
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
        # cur.execute(
        #     """
        #     UPDATE users
        #     SET email = %(email)s, picture_url = %(picture_url)s
        #     WHERE id = %(id)s
        #     RETURNING id
        #     """,
        #     args_dic
        # )
        args_dic['id'] = id
        query =sql.Composed(update_lst)
        cursor = ClientCursor(create_pool().getconn())
        print('mogrify123', cursor.mogrify(query, args_dic), file=sys.stdout)
        cur.execute(
            query,
            args_dic
        )
        result = cur.fetchone()
        cur.close()
        return result['id']
    except Exception as e:
        return None
def update_user(pool, args_dic, id: str):
    return run_query(pool, lambda cur: update_user_query(cur, args_dic, id))
