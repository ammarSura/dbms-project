routes
- getListings
  filters- price, type of place, rooms, beds, bathrooms, amenities,prop type, etc
- getListingDetails
  ensure calendar only shows available slots.
- getHost
- postBooking
- postWishlist
- getUser
- getBookingDetails
- getWishlist
- postReview
- getReviews
- postUser

entities

Listings breakdown
 - Neighbourhood: id, neighbourhood, latitude, longitude, neighbourhood_cleansed, listing_id
 - Listing: id, name, description, neighborhood_overview, picture_url, host_id
 - Listing_Details: (ensure this does not include filter params) listing_id, property_type, room_type, accomodates_no, bathrooms(need to parse this from bathroom_text), bedrooms, beds, amenities, price, min_nights, max_nights, has_availability, num_of_reviews, review_rating, instanst_bookable,
 - Host: id, name, host_since, host_location, host_about, response_time, response_rate, acceptance_rate, is_super_host, picture_url, neighbourhood, listings_count, identity_verified

