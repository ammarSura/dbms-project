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
    """,
    """
        ALTER TABLE bookings ADD CONSTRAINT check_dates CHECK (start_date < end_date AND end_date > CURRENT_DATE);
    """,
    """
        ALTER TABLE bookings ADD CONSTRAINT check_cost CHECK (cost > 0);
    """,
    """
        ALTER TABLE reviews ADD COLUMN IF NOT EXISTS rating NUMERIC(3, 2) DEFAULT 0.00;
    """,
    """
        ALTER TABLE bookings ADD COLUMN IF NOT EXISTS num_guests SMALLINT DEFAULT 1;
    """,
    """
        ALTER TABLE users
        ALTER COLUMN created_at SET DEFAULT current_timestamp,
        ALTER COLUMN updated_at SET DEFAULT current_timestamp;
    """,
    """
        ALTER TABLE reviews
        ALTER COLUMN created_at SET DEFAULT current_timestamp
    """,
     """
        ALTER TABLE hosts
        ALTER COLUMN host_since SET DEFAULT current_timestamp,
        ALTER COLUMN updated_at SET DEFAULT current_timestamp;
    """,
     """
        ALTER TABLE bookings
        ALTER COLUMN created_at SET DEFAULT current_timestamp,
        ALTER COLUMN updated_at SET DEFAULT current_timestamp;
    """,
     """
        ALTER TABLE listings
        ALTER COLUMN created_at SET DEFAULT current_timestamp,
        ALTER COLUMN updated_at SET DEFAULT current_timestamp;
    """,

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
        SELECT l1.id, l1."name", l1.room_type, l1.property_type, l1.description, l1.accommodates, l1.picture_url, l1.price, l1.neighbourhood, l1.rating, reviews."comments", reviews.reviewer_id, u."name" reviewer_name, reviews.created_at as latest_review FROM listings l1
        INNER JOIN (
            SELECT l.id, AVG(l.rating) average_rating FROM listings l
            where l.rating is not null
            group by l.id
            order by AVG(l.rating) DESC
            limit 200
        ) l2 on l1.id = l2.id
        LEFT JOIN reviews ON l1.id = reviews.listing_id
        LEFT JOIN users u on u.id = reviews.reviewer_id
        WHERE reviews.created_at = (select max(r.created_at) FROM reviews r WHERE r.listing_id = l1.id)
        ORDER BY l2.average_rating desc
    """,
    """
        CREATE MATERIALIZED VIEW IF NOT EXISTS best_hosts AS
            SELECT top_hosts.*, top_listings.top_listings_id, top_listings.max_rating FROM (
                SELECT h.id, AVG(l.rating) avg_rating, u."name", u.picture_url FROM "hosts" h
                LEFT JOIN listings l on l.host_id = h.id
                LEFT JOIN users u on u.id = h.user_id
                WHERE h.is_superhost = true
                AND l.rating IS NOT NULL
                GROUP BY h.id, u."name", u.picture_url
                ORDER BY avg_rating desc
            ) AS top_hosts
            LEFT JOIN (
                SELECT h.id AS host_id, l.id AS top_listings_id, l.rating AS max_rating
                FROM hosts h
                LEFT JOIN listings l ON h.id = l.host_id
                WHERE l.rating = (
                    SELECT MAX(rating) FROM listings WHERE host_id = h.id
                )
            ) AS top_listings ON top_listings.host_id = top_hosts.id
            ORDER BY top_hosts.avg_rating DESC;
    """
]

for query in create_table_lst:
    try:
        run_query(pool, lambda cur: cur.execute(query))
    except Exception as e:
        print(e)
        print(query)

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
