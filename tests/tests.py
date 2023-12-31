import logging
import unittest
from decimal import Decimal
from typing import Callable

from update_host import update_host

from update_user import update_user

from get_booking import get_bookings

from post_booking import post_booking

from get_reviews import get_reviews

from post_review import post_review

from get_best_hosts import get_best_hosts
from get_best_listings import get_best_listing

from faker import Faker
from psycopg import Connection, sql

from utils.db_utils import create_pool
from get_host import get_host
from get_listing import get_listing
from get_user import get_user
from post_host import post_host
from post_listing import post_listing
from post_user import post_user
from utils.test_utils import (create_fake_booking, create_fake_host,
                              create_fake_listing, create_fake_review, create_fake_user, delete_keys)


class MethodTester(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.pool = create_pool()
        logging.getLogger('faker').setLevel(logging.ERROR)
        self.logger = logging.getLogger().setLevel(logging.CRITICAL)
        fake = Faker()
        self.fake = fake

    def setUp(self):
        random_user = create_fake_user(self.fake)
        if (random_user.get('name') == None):
            raise Exception('Name is required')
        user_id = post_user(self.pool, random_user, self.logger)
        self.test_user = get_user(self.pool, {
            'id': user_id
        })

    def _test_get_item(self, test_gen: Callable[[Faker], dict], equality_check: Callable[[dict, dict], bool], post_item: Callable[[Connection, dict, logging.Logger], int or None], get_item: Callable[[Connection, dict], dict or list or None]):
        test_item = test_gen(self.fake)
        posted_item_id = post_item(self.pool, test_item, self.logger)
        self.assertIsNotNone(posted_item_id)
        fetched_items = get_item(self.pool, {
            'id': posted_item_id
        })
        fetched_item = fetched_items[0] if isinstance(
            fetched_items, list) else fetched_items
        equality_check(test_item, fetched_item)
        return posted_item_id

    def _test_get_items(self, test_gen: Callable[[Faker], dict], equality_check: Callable[[dict, dict], bool], post_item: Callable[[Connection, dict, logging.Logger], int or None], get_item: Callable[[Connection, dict], dict or list or None], args_dic: dict):
        result = list(map(lambda _: self._test_get_item(
            test_gen, equality_check, post_item, get_item), [0] * 11))
        listings = get_item(self.pool, args_dic)
        self.assertEqual(len(listings), 11)

        return listings

    def _test_get_item_invalid_param(self, test_gen: Callable[[Faker], dict], post_item: Callable[[Connection, dict], int or None], get_item: Callable[[Connection, dict], dict or list or None]):
        return
        test_item = test_gen(self.fake)
        posted_item_id = post_item(self.pool, test_item, self.logger)
        fetched_items = get_item(self.pool, {
            'id': self.fake.random_int(0, 1000000)
        })
        fetched_item = fetched_items[0] if isinstance(
            fetched_items, list) and len(fetched_items) > 0 else fetched_items
        if (fetched_item is not None):
            self.assertNotEqual(fetched_item['id'], posted_item_id)

    def _test_post_item(self, test_gen: Callable[[Faker], dict], post_item: Callable[[Connection, dict, logging.Logger], int or None], get_item: Callable[[Connection, dict], dict or list or None]):
        new_item = test_gen(self.fake)
        posted_item_id = post_item(self.pool, new_item, self.logger)
        self.assertIsNotNone(posted_item_id)
        fetched_items = get_item(self.pool, {
            'id': posted_item_id
        })
        fetched_item = fetched_items[0] if isinstance(
            fetched_items, list) else fetched_items
        self.assertIsNotNone(fetched_item)
        self.assertEqual(fetched_item['id'], posted_item_id)

    def _test_post_item_missing_required_param(self, required_param: str, test_gen: Callable[[Faker], dict], post_item: Callable[[Connection, dict, logging.Logger], int or None]):
        pass
        new_item = test_gen(self.fake)
        new_item[required_param] = None
        posted_item_id = post_item(self.pool, new_item, self.logger)
        self.assertIsNone(posted_item_id)

    def _test_post_item_missing_param(self, param: str, test_gen: Callable[[Faker], dict], post_item: Callable[[Connection, dict, logging.Logger], int or None]):
        pass
        new_item = test_gen(self.fake)
        del new_item[param]
        posted_item_id = post_item(self.pool, new_item, self.logger)
        self.assertIsNotNone(posted_item_id)


class TestUserMethods(MethodTester):
    def user_equality_check(self, test_user: dict, fetched_user: dict or None):
        self.assertIsNotNone(fetched_user)
        self.assertIsNotNone(fetched_user['created_at'])
        self.assertIsNotNone(fetched_user['updated_at'])
        del fetched_user['created_at']
        del fetched_user['updated_at']
        del fetched_user['id']
        del test_user['password']
        del fetched_user['password']
        self.assertDictEqual(test_user, fetched_user)

    def test_get_user(self):
        self._test_get_item(
            create_fake_user, self.user_equality_check, post_user, get_user)

    def test_get_user_missing_param(self):
        self._test_get_item_invalid_param(
            create_fake_user, post_user, get_user)

    def test_post_user(self):
        self._test_post_item(create_fake_user, post_user, get_user)

    def test_post_user_missing_required_param(self):
        return self._test_post_item_missing_required_param('name', create_fake_user, post_user)

    def test_post_user_missing_param(self):
        return self._test_post_item_missing_param('picture_url', create_fake_user, post_user)

    def test_update_user(self):
        update = {
            'email': self.fake.unique.email(),
            'picture_url': self.fake.url()
        }
        updated_id = update_user(self.pool, update, self.test_user['id'])
        self.assertEqual(updated_id, self.test_user['id'])
        fetched_user = get_user(self.pool, {
            'id': self.test_user['id']
        })

        self.assertEqual(update['email'], fetched_user['email'])
        self.assertEqual(update['picture_url'], fetched_user['picture_url'])


class TestHostMethods(MethodTester):
    def host_equality_check(self, test_host: dict, fetched_host: dict or None):
        self.assertIsNotNone(fetched_host)
        self.assertIsNotNone(fetched_host['host_since'])
        self.assertIsNotNone(fetched_host['updated_at'])
        acceptance_rate = fetched_host['acceptance_rate'], test_host['acceptance_rate']
        response_rate = fetched_host['response_rate'], test_host['response_rate']
        self.assertAlmostEqual(acceptance_rate[0], Decimal(acceptance_rate[1]))
        self.assertAlmostEqual(response_rate[0], Decimal(response_rate[1]))
        del fetched_host['id'], fetched_host['host_since'], fetched_host['updated_at']
        del fetched_host['acceptance_rate'], fetched_host['response_rate']
        del test_host['response_rate'], test_host['acceptance_rate']

        self.assertDictEqual(test_host, fetched_host)

    def create_fake_host_with_user_id(self):
        test_user_id = self.test_user['id']
        return lambda faker: create_fake_host(faker, test_user_id)

    def test_get_host(self):
        self._test_get_item(self.create_fake_host_with_user_id(
        ), self.host_equality_check, post_host, get_host)

    def test_get_host_missing_param(self):
        self._test_get_item_invalid_param(
            self.create_fake_host_with_user_id(), post_host, get_host)

    def test_post_host(self):
        self._test_post_item(
            self.create_fake_host_with_user_id(), post_host, get_host)

    def test_post_host_missing_required_param(self):
        self._test_post_item_missing_required_param(
            'user_id', self.create_fake_host_with_user_id(), post_host)

    def test_post_host_missing_param(self):
        self._test_post_item_missing_param(
            'about', self.create_fake_host_with_user_id(), post_host)

    def test_update_host(self):
        update = {
            'about': self.fake.text()
        }
        test_host_id = self._test_get_item(self.create_fake_host_with_user_id(
        ), self.host_equality_check, post_host, get_host)
        test_host_before_update = get_host(self.pool, {
            'id': test_host_id
        })
        host_id = update_host(self.pool, update, test_host_id)
        self.assertEqual(host_id, test_host_id)
        test_host_after_update = get_host(self.pool, {
            'id': test_host_id
        })
        self.assertEqual(
            test_host_before_update['id'], test_host_after_update['id'])
        self.assertEqual(test_host_after_update['about'], update['about'])


class TestListingMethods(MethodTester):
    def listing_equality_check(self, test_listing: dict, fetched_listing: dict or None):
        self.maxDiff = None
        self.assertIsNotNone(fetched_listing)
        self.assertIsNotNone(fetched_listing['created_at'])
        self.assertIsNotNone(fetched_listing['updated_at'])
        self.assertAlmostEqual(
            fetched_listing['price'], Decimal(test_listing['price']))
        self.assertAlmostEqual(fetched_listing['rating'], Decimal(
            test_listing['rating']))
        self.assertListEqual(
            test_listing['amenities'], fetched_listing['amenities'])
        delete_keys(fetched_listing, [
                    'id', 'created_at', 'updated_at', 'price', 'rating', 'amenities', 'description', 'min_nights', 'max_nights'])
        delete_keys(test_listing, ['price', 'rating', 'amenities', 'coord'])
        self.assertDictEqual(test_listing, fetched_listing)

    def create_fake_listing_with_host_id(self):
        test_user_id = self.test_user['id']
        new_host = create_fake_host(self.fake, test_user_id)
        new_host_id = post_host(self.pool, new_host, self.logger)

        return lambda faker: create_fake_listing(faker, new_host_id)

    def test_get_listings1(self):
        print('xqwe')
        listing_id = self._test_get_item(self.create_fake_listing_with_host_id(
        ), self.listing_equality_check, post_listing, get_listing)

        fetched_listing = get_listing(self.pool, {
            'id': listing_id,
            'extra_fields': [
                sql.Identifier('hosts', 'is_superhost'),
                sql.Identifier('reviews', 'id'),
                sql.Identifier('reviews', 'comments'),
                sql.Identifier('reviews', 'rating'),
                sql.Identifier('reviews', 'created_at'),
                sql.Identifier('reviews', 'reviewer_id'),
                sql.Identifier('users', 'name'),
                sql.Identifier('users', 'picture_url'),
            ],
            'extra_query': {
                'query_lst': [
                    sql.SQL("\nINNER JOIN hosts ON hosts.id = listings.host_id"),
                    sql.SQL(
                        "\nLEFT JOIN reviews ON reviews.listing_id = listings.id"),
                    sql.SQL("\nINNER JOIN users ON users.id = reviews.reviewer_id")
                ]}
        })
        print('HEX', fetched_listing)

    def test_get_listings_missing_param(self):
        self._test_get_item_invalid_param(
            self.create_fake_listing_with_host_id(), post_listing, get_listing)

    def test_post_listings(self):
        self._test_post_item(
            self.create_fake_listing_with_host_id(), post_listing, get_listing)

    def test_post_listings_missing_required_param(self):
        self._test_post_item_missing_required_param(
            'host_id', self.create_fake_listing_with_host_id(), post_listing)

    def test_post_listings_missing_param(self):
        self._test_post_item_missing_param(
            'bedrooms', self.create_fake_listing_with_host_id(), post_listing)

    def test_get_listings(self):
        args_dic = {
            'count': 11,
        }

        extra_query = []
        extra_query.append(
            sql.SQL("\nINNER JOIN hosts ON hosts.id = listings.host_id")
        )
        extra_query.append(
            sql.SQL("\nWHERE hosts.is_superhost = %(is_superhost)s")
        )
        extra_query.append(
            sql.SQL("\nAND price >= %(min_price)s")
        )
        extra_query.append(
            sql.SQL("\nAND listings.id NOT IN (SELECT DISTINCT listing_id FROM bookings WHERE start_date <= %(check_in)s AND end_date >= %(check_in)s AND listing_id = listings.id)")
        )

        args_dic['extra_query'] = {
            'query_lst': extra_query,
            'args_dic': {
                'is_superhost': True,
                'min_price': 100,
                'check_in': '2021-04-01',
                'check_out': '2021-04-10'
            }
        }
        # self.assertGreaterEqual(len(listings_with_args), 1)
        listings_with_args = get_listing(self.pool, args_dic)
        # found_item = next(
        #     item for item in listings_with_args if item["id"] == listings[0]["id"])
        # self.assertIsNotNone(found_item)
        # self.assertEqual(found_item['id'], listings[0]['id'])


class TestAnalyticsMethods(MethodTester):
    def test_best_listings_query(self):
        query_lst = [
            sql.SQL('WHERE best_listings.price < %(price)s')
        ]
        query_lst_args = {
            'price': 100000
        }
        extra_query = {
            'query_lst': query_lst,
            'args_dic': query_lst_args
        }
        listings = get_best_listing(self.pool, {
            'count': 10,
            'extra_query': extra_query
        })
        self.assertIsNotNone(listings)
        self.assertTrue(isinstance(listings, list))
        self.assertGreaterEqual(len(listings), 10)

    def test_best_hosts_query(self):
        hosts = get_best_hosts(self.pool, {
            'count': 10
        })
        self.assertIsNotNone(hosts)
        self.assertTrue(isinstance(hosts, list))
        self.assertEqual(len(hosts), 10)


class TestReviewsMethods(MethodTester):
    def create_fake_review_with_user_id(self):
        test_user_id = self.test_user['id']
        new_host = create_fake_host(self.fake, test_user_id)
        new_host_id = post_host(self.pool, new_host, self.logger)
        new_listing = create_fake_listing(self.fake, new_host_id)
        new_listing_id = post_listing(self.pool, new_listing, self.logger)
        return lambda faker: create_fake_review(faker, new_listing_id, test_user_id)

    def equality_check(self, test_listing: dict, fetched_listing: dict or None):
        self.assertIsNotNone(fetched_listing)
        self.assertIsNotNone(fetched_listing['created_at'])
        self.assertIsNotNone(fetched_listing['id'])
        self.assertAlmostEqual(
            fetched_listing['rating'], Decimal(test_listing['rating']))
        self.assertEqual(
            fetched_listing['listing_id'], test_listing['listing_id'])
        self.assertEqual(
            fetched_listing['reviewer_id'], test_listing['reviewer_id'])
        self.assertEqual(fetched_listing['comments'], test_listing['comments'])

    def test_get_review(self):
        self._test_get_item(self.create_fake_review_with_user_id(
        ), self.equality_check, post_review, get_reviews)

    def test_get_reviews_missing_param(self):
        self._test_get_item_invalid_param(
            self.create_fake_review_with_user_id(), post_review, get_reviews)

    def test_post_reviews(self):
        self._test_post_item(
            self.create_fake_review_with_user_id(), post_review, get_reviews)

    def test_post_reviews_missing_required_param(self):
        self._test_post_item_missing_required_param(
            'listing_id', self.create_fake_review_with_user_id(), post_review)

    def test_get_reviews(self):
        self._test_get_items(self.create_fake_review_with_user_id(
        ), self.equality_check, post_review, get_reviews, {'count': 11})


class TestBookingMethods(MethodTester):
    def create_fake_booking_with_user_id(self):
        test_user_id = self.test_user['id']
        new_host = create_fake_host(self.fake, test_user_id)
        new_host_id = post_host(self.pool, new_host, self.logger)
        new_listing = create_fake_listing(self.fake, new_host_id)
        new_listing_id = post_listing(self.pool, new_listing, self.logger)
        return lambda faker: create_fake_booking(faker, new_listing_id, test_user_id)

    def equality_check(self, test_listing: dict, fetched_listing: dict or None):
        self.assertIsNotNone(fetched_listing)
        self.assertIsNotNone(fetched_listing['created_at'])
        self.assertIsNotNone(fetched_listing['id'])
        self.assertAlmostEqual(
            fetched_listing['cost'], Decimal(test_listing['cost']))
        self.assertEqual(
            fetched_listing['listing_id'], test_listing['listing_id'])
        self.assertEqual(
            fetched_listing['booker_id'], test_listing['booker_id'])
        # self.assertEqual(fetched_listing['start_date'], test_listing['start_date'])
        # self.assert(fetched_listing['end_date'], test_listing['end_date'])
        pass

    def test_get_booking(self):
        booking_id = self._test_get_item(self.create_fake_booking_with_user_id(
        ), self.equality_check, post_booking, get_bookings)
        self.assertIsNotNone(booking_id)
        booking = get_bookings(self.pool, {
            'id': booking_id,
            'extra_query': {
                'query_lst': [
                    sql.SQL(
                        '\nLEFT JOIN listings ON listings.id = bookings.listing_id'),
                ],
                'args_dic': {
                    'host_id': self.test_user['id']
                }
            },
            'extra_fields': [
                sql.Identifier('listings', 'host_id')
            ]
        })
        self.assertIsNotNone(booking)
        self.assertEqual(booking['id'], booking_id)
        booking = get_bookings(self.pool, {
            'extra_query': {
                'query_lst': [
                    sql.SQL(
                        '\nLEFT JOIN listings ON listings.id = bookings.listing_id'),
                    sql.SQL('\nWHERE listings.host_id = %(host_id)s'),
                ],
                'args_dic': {
                    'host_id': booking['host_id']
                }
            }
        })
        print(booking)

    def test_get_booking_missing_param(self):
        self._test_get_item_invalid_param(
            self.create_fake_booking_with_user_id(), post_booking, get_bookings)

    def test_post_booking(self):
        self._test_post_item(
            self.create_fake_booking_with_user_id(), post_booking, get_bookings)

    def test_get_bookings(self):
        self._test_get_items(self.create_fake_booking_with_user_id(
        ), self.equality_check, post_booking, get_bookings, {'count': 11})


class TestSQLInjection(MethodTester):
    def _tester(self, name):
        new_user = create_fake_user(self.fake)
        new_user['name'] = name
        id = post_user(self.pool, new_user, self.logger)
        self.assertIsNotNone(id)

    def test_get_user_sanity(self):
        test_strings = [
            "Ammar's test",
            "Ammar's test'; DROP TABLE users;",
            "Ammar's --;"
        ]
        for i in test_strings:
            self._tester(i)


if __name__ == '__main__':
    unittest.main()
    print('Starting tests')
