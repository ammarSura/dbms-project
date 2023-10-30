from psycopg import Cursor

from db_utils import create_pool, run_query

pool = create_pool()
create_table_lst = [
    """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            is_host BOOL DEFAULT FALSE,
            picture_url VARCHAR(150),
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(32) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS hosts (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            location VARCHAR(250) DEFAULT NULL,
            neighbourhood VARCHAR(250) DEFAULT NULL,
            about TEXT DEFAULT NULL,
            response_time VARCHAR(50) DEFAULT NULL,
            response_rate NUMERIC(5, 2) DEFAULT NULL,
            acceptance_rate NUMERIC(5, 2) DEFAULT NULL,
            is_superhost BOOLEAN DEFAULT FALSE,
            identity_verified BOOLEAN DEFAULT FALSE,
            host_since TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_user
                FOREIGN KEY(user_id)
	                REFERENCES users
                    ON DELETE CASCADE
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS listings (
            id BIGSERIAL PRIMARY KEY,
            host_id INT NOT NULL,
            name VARCHAR(150) NOT NULL,
            description TEXT DEFAULT NULL,
            location VARCHAR(100) NOT NULL,
            neighbourhood VARCHAR(250) DEFAULT NULL,
            neighbourhood_overview TEXT DEFAULT NULL,
            coord POINT NOT NULL,
            property_type VARCHAR(50) NOT NULL,
            room_type VARCHAR(50) NOT NULL,
            accommodates SMALLINT DEFAULT 1,
            bathrooms VARCHAR(50) DEFAULT NULL,
            bedrooms SMALLINT DEFAULT 1,
            beds SMALLINT DEFAULT 1,
            amenities VARCHAR(300)[] DEFAULT NULL,
            price NUMERIC(10, 2) NOT NULL,
            min_nights SMALLINT DEFAULT 1,
            max_nights SMALLINT DEFAULT 365,
            rating NUMERIC(3, 2) DEFAULT 0.00,
            picture_url VARCHAR(150) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_host
                FOREIGN KEY(host_id)
	                REFERENCES hosts
                    ON DELETE CASCADE
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS reviews (
            id BIGSERIAL PRIMARY KEY,
            listing_id BIGINT NOT NULL,
            reviewer_id INT NOT NULL,
            comments TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_listing
                FOREIGN KEY(listing_id)
                    REFERENCES listings
                    ON DELETE CASCADE,
            CONSTRAINT fk_reviewer_id
                FOREIGN KEY(reviewer_id)
                    REFERENCES users
        );
    """,
    """
        CREATE TABLE IF NOT EXISTS bookings (
        id SERIAL PRIMARY KEY,
        booker_id INT NOT NULL,
        listing_id BIGINT NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        cost NUMERIC(10, 2) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_booker
            FOREIGN KEY(booker_id)
                REFERENCES users,
        CONSTRAINT fk_listing
            FOREIGN KEY(listing_id)
                REFERENCES listings
        );
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
        SELECT listing.id, listing."name", listing.room_type, listing.listing.property_type, listing.description, listing.accommodates, listing.picture_url, price, neighborhood, review_rating, review."comments", review.reviewer_id, min(review.created_at) as latest_review FROM listing
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
    """,

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
