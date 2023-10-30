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
        CREATE INDEX IF NOT EXISTS host_user_id ON hosts(user_id)
    """,
    """
        CREATE INDEX IF NOT EXISTS listing_host_id ON listings(host_id)
    """,
    """
        CREATE INDEX IF NOT EXISTS listing_price ON listings(price)
    """,
    """
        CREATE INDEX IF NOT EXISTS listing_neighborhood ON listings(neighbourhood)
    """,
    """
        CREATE INDEX IF NOT EXISTS listing_bathrooms ON listings(bathrooms)
    """,
    """
        CREATE INDEX IF NOT EXISTS review_listing_id ON reviews(listing_id)
    """,
    """
        CREATE INDEX IF NOT EXISTS review_reviewer_id ON reviews(reviewer_id)
    """
]

create_materialized_view_lst = [
    """
        CREATE MATERIALIZED VIEW IF NOT EXISTS best_listings AS
        SELECT listings.id, listings."name", listings.room_type, listings.property_type, listings.description, listings.accommodates, listings.picture_url, price, listings.neighbourhood, listings.rating, reviews."comments", reviews.reviewer_id, min(reviews.created_at) as latest_review FROM listings
        LEFT JOIN reviews ON listings.id = reviews.listing_id
        LEFT JOIN users u on u.id = reviews.reviewer_id
        GROUP BY listings.id, reviews.reviewer_id, reviews."comments"
        ORDER BY rating DESC
        LIMIT 200;
    """,
    """
        CREATE MATERIALIZED VIEW IF NOT EXISTS best_hosts AS
        SELECT h.id, avg(l.rating), h.host_since, u."name", u.picture_url FROM "hosts" h
        LEFT JOIN listings l on l.host_id = h.id
        LEFT JOIN users u on u.id = h.user_id
        WHERE h.is_superhost = true
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
