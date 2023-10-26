from psycopg import Cursor
from db_utils import run_query, create_pool

pool = create_pool()
create_table_lst = [
    """
        CREATE TABLE IF NOT EXISTS host (
            id SERIAL PRIMARY KEY,
            host_since DATE,
            location VARCHAR(150),
            about VARCHAR(500),
            response_time VARCHAR(50),
            response_rate REAL,
            acceptance_rate REAL,
            is_super_host BOOLEAN,
            neighbourhood VARCHAR(100),
            listings_count INT,
            identity_verified BOOLEAN
        )
    """
    ,
    """
       CREATE TABLE IF NOT EXISTS listing (
            id SERIAL PRIMARY KEY,
            name VARCHAR(150) NOT NULL,
            picture_url VARCHAR(150) NOT NULL,
            coors POINT NOT NULL,
            price MONEY NOT NULL,
            property_type VARCHAR(50) NOT NULL,
            room_type VARCHAR(50) NOT NULL,
            accommodates SMALLINT NOT NULL,
            bathrooms SMALLINT,
            bedrooms SMALLINT,
            beds SMALLINT,
            bed_type VARCHAR(50) NOT NULL,
            amenities VARCHAR(75) NOT NULL,
            host_id INT NOT NULL,
            CONSTRAINT fk_host
                FOREIGN KEY(host_id)
	                REFERENCES host
                    ON DELETE CASCADE
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS "users" (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            picture_url VARCHAR(150),
            host_id INT NOT NULL,
            CONSTRAINT fk_host
                FOREIGN KEY(host_id)
	                REFERENCES host
                    ON DELETE CASCADE
        )
    """
]

for query in create_table_lst:
    run_query(pool, lambda cur: cur.execute(query))
