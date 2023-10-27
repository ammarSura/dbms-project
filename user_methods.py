from psycopg import Cursor
import sys


def get_user(cur: Cursor, args_dic: dict):
    cur.execute("""
        SELECT * FROM users
        WHERE id = %s
    """
    , [args_dic['id']])
    result = cur.fetchone()
    user = {
        'id': result[0],
        'name': result[1],
        'picture_url': result[2]
    }
    return user

def post_user(cur: Cursor, args_dic: dict):
    try:
        cur.execute("""
            INSERT INTO users (name, picture_url, email, password)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        , [
            args_dic['name'],
            args_dic['picture_url'],
            args_dic['email'],
            args_dic['password']
        ])
        result = cur.fetchone()
        print(result, file=sys.stdout)
        return result[0]
    except Exception as e:
        print('Missing param', e, file=sys.stdout)
        return None
