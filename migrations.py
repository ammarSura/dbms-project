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
            host_since DATE,
            location VARCHAR(150),
            about VARCHAR(500),
            response_time VARCHAR(50),
            response_rate NUMERIC(5, 2),
            acceptance_rate NUMERIC(5, 2),
            is_super_host BOOLEAN,
            identity_verified BOOLEAN,
            user_id INT,
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
            amenities VARCHAR(75) NOT NULL,
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
            id PRIMARY KEY,
            date DATE NOT NULL,
            comments VARCHAR(500),
            listing_id INT NOT NULL,
            reviewer_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_listing
                FOREIGN KEY(listing_id)
                    REFERENCES listing
                    ON DELETE CASCADE
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
                REFERENCES users
        CONSTRAINT fk_listing
            FOREIGN KEY(listing_id)
                REFERENCES listing
        )
    """
]

create_index_lst = [
    """
        CREATE INDEX listing_price ON listing(price)
    """
]
for query in create_table_lst:
    run_query(pool, lambda cur: cur.execute(query))
