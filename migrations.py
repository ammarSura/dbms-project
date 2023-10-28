from psycopg import Cursor
from db_utils import run_query, create_pool

pool = create_pool()
create_table_lst = [
    """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            picture_url VARCHAR(150),
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(20) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    ,
    """
        CREATE TABLE IF NOT EXISTS host (
            id SERIAL PRIMARY KEY,
            about VARCHAR(500),
            response_time VARCHAR(50),
            response_rate NUMERIC(5, 2),
            acceptance_rate NUMERIC(5, 2),
            is_super_host BOOLEAN,
            identity_verified BOOLEAN,
            user_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_user
                FOREIGN KEY(user_id)
	                REFERENCES users
                    ON DELETE CASCADE
        )
    """
    ,
    """
       CREATE TABLE IF NOT EXISTS listing (
            id SERIAL PRIMARY KEY,
            name VARCHAR(150) NOT NULL,
            picture_url VARCHAR(150) NOT NULL,
            coors POINT NOT NULL,
            price NUMERIC(10, 2) NOT NULL,
            property_type VARCHAR(50) NOT NULL,
            room_type VARCHAR(50) NOT NULL,
            accommodates SMALLINT NOT NULL,
            bathrooms VARCHAR(50),
            bedrooms SMALLINT,
            beds SMALLINT NOT NULL,
            bed_type VARCHAR(50) NOT NULL,
            amenities VARCHAR(75)[] NOT NULL,
            host_id INT NOT NULL,
            neighborhood VARCHAR(50),
            neighborhood_overview VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            review_rating NUMERIC(3, 2),
            review_cleanliness NUMERIC(3, 2),
            review_checking NUMERIC(3, 2),
            review_communication NUMERIC(3, 2),
            review_location NUMERIC(3, 2),
            review_value NUMERIC(3, 2),
            CONSTRAINT fk_host
                FOREIGN KEY(host_id)
	                REFERENCES host
                    ON DELETE CASCADE
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS review (
            id SERIAL PRIMARY KEY,
            comments VARCHAR(500),
            listing_id INT NOT NULL,
            reviewer_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_listing
                FOREIGN KEY(listing_id)
                    REFERENCES listing
                    ON DELETE CASCADE,
            CONSTRAINT fk_reviewer_id
                FOREIGN KEY(reviewer_id)
                    REFERENCES users
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS booking (
        id SERIAL PRIMARY KEY,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        cost NUMERIC(10, 2) NOT NULL,
        booker_id INT NOT NULL,
        listing_id INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_booker
            FOREIGN KEY(booker_id)
                REFERENCES users,
        CONSTRAINT fk_listing
            FOREIGN KEY(listing_id)
                REFERENCES listing
        )
    """,
    """
        ALTER TABLE host
        ALTER COLUMN user_id SET NOT NULL;
    """,
    """
        ALTER TABLE listing
        DROP COLUMN IF EXISTS review_cleanliness,
        DROP COLUMN IF EXISTS review_checking,
        DROP COLUMN IF EXISTS review_communication,
        DROP COLUMN IF EXISTS review_location,
        DROP COLUMN IF EXISTS review_value;
    """
]

create_index_lst = [
    """
        CREATE INDEX IF NOT EXISTS host_user_id ON host(user_id)
    """,
    """
        CREATE INDEX IF NOT EXISTS listing_host_id ON listing(host_id)
    """,
    """
        CREATE INDEX IF NOT EXISTS listing_price ON listing(price)
    """,
    """
        CREATE INDEX IF NOT EXISTS listing_neighborhood ON listing(neighborhood)
    """,
    """
        CREATE INDEX IF NOT EXISTS listing_bathrooms ON listing(bathrooms)
    """,
    """
        CREATE INDEX IF NOT EXISTS review_listing_id ON review(listing_id)
    """,
    """
        CREATE INDEX IF NOT EXISTS review_reviewer_id ON review(reviewer_id)
    """
]

create_materialized_view_lst = [
    """
        CREATE MATERIALIZED VIEW IF NOT EXISTS best_listings AS
        SELECT listing.id, listing."name", listing.picture_url, price, neighborhood, review_rating, review."comments", review.reviewer_id, min(review.created_at) as latest_review FROM listing
        LEFT JOIN review ON listing.id = review.listing_id
        LEFT JOIN users u on u.id = review.reviewer_id
        GROUP BY listing.id, review.reviewer_id, review."comments"
        ORDER BY review_rating DESC
        LIMIT 200;
    """,
    """
        CREATE MATERIALIZED VIEW IF NOT EXISTS best_hosts AS
        SELECT h.id, avg(l.review_rating), h.created_at, u."name", u.picture_url FROM "host" h
        LEFT JOIN listing l on l.host_id = h.id
        LEFT JOIN users u on u.id = h.user_id
        WHERE h.is_super_host = true
        GROUP BY h.id, u."name", u.picture_url
        ORDER BY avg DESC
        LIMIT 200;
    """
    ,

]
for query in create_table_lst:
    try:
        run_query(pool, lambda cur: cur.execute(query))
    except Exception as e:
        print(e)
        print(query)
        break

for query in create_index_lst:
    try:
        run_query(pool, lambda cur: cur.execute(query))
    except Exception as e:
        print(e)
        print(query)
        break
for query in create_materialized_view_lst:
    try:
        run_query(pool, lambda cur: cur.execute(query))
    except Exception as e:
        print(e)
        print(query)
        break
