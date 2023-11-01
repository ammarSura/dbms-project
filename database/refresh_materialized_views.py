from utils.db_utils import run_query, create_pool

refreshes = [
    "REFRESH MATERIALIZED view best_hosts WITH data",
    "REFRESH MATERIALIZED view best_listings WITH data",
]
pool = create_pool()
for refresh in refreshes:
    run_query(pool, lambda cur: cur.execute(refresh))
