from utils.db_utils import run_query, update_query


def update_host(pool, args_dic, id: str):
    return run_query(pool, lambda cur: update_query(cur, args_dic, id, 'hosts'))
