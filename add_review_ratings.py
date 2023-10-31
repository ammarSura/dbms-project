from db_utils import create_pool


pool = create_pool()

query_lst = [
    """
        UPDATE reviews
        SET rating = listings.rating
        FROM listings
        WHERE reviews.listing_id = listings.id;
    """
]

with pool.cursor() as cur:
    for query in query_lst:
        cur.execute(query)
    pool.commit()
    pool.closeall()
