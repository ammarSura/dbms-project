from utils.db_utils import create_pool, run_query


pool = create_pool()

query_lst = [
    """
        UPDATE reviews
        SET rating = listings.rating
        FROM listings
        WHERE reviews.listing_id = listings.id;
    """
]

for query in query_lst:
    try:
        run_query(pool, lambda cur: cur.execute(query))
    except Exception as e:
        print(e)
        print(query)
        break
