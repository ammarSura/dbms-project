from db_utils import create_pool, run_query


func_lst = [
    """
		CREATE OR REPLACE FUNCTION update_listing_avg_rating()
		RETURNS trigger
		LANGUAGE plpgsql
		AS
		$$
			BEGIN
			-- Calculate the new average rating for the given listing_id
			UPDATE listings
			SET rating = (
				SELECT AVG(rating)
				FROM reviews
				WHERE listing_id = NEW.listing_id
			)
			WHERE id = NEW.listing_id;

			RETURN NEW;
			END;
		$$;
    """,
	"""
		CREATE or replace TRIGGER rating_added
		AFTER insert
		ON reviews
		FOR EACH ROW
		EXECUTE PROCEDURE update_listing_avg_rating();
	"""
]

pool = create_pool()
for query in func_lst:
	run_query(pool, lambda cur: cur.execute(query))
