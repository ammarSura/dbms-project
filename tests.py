import logging
import unittest
from decimal import Decimal
from typing import Callable

from get_reviews import get_reviews

from post_review import post_review

from get_best_hosts import get_best_hosts
from get_best_listings import get_best_listing

from faker import Faker
from psycopg import Connection, sql

from db_utils import create_pool
from get_host import get_host
from get_listing import get_listing
from get_user import get_user
from post_host import post_host
from post_listing import post_listing
from post_user import post_user
from test_utils import (create_fake_host, create_fake_listing, create_fake_review, create_fake_user, delete_keys)

class MethodTester(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.pool = create_pool()
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('faker').setLevel(logging.ERROR)
        self.logger = logging.getLogger()
        fake = Faker()
        self.fake = fake

    def setUp(self):
        random_user = create_fake_user(self.fake)
        user_id = post_user(self.pool, random_user, self.logger)
        self.test_user = get_user(self.pool, {
            'id': user_id
        })

    def _test_get_item(self, test_gen: Callable[[Faker], dict], equality_check: Callable[[dict, dict], bool], post_item: Callable[[Connection, dict, logging.Logger], int or None], get_item: Callable[[Connection, dict], dict or list or None]):
        test_item = test_gen(self.fake)
        posted_item_id = post_item(self.pool, test_item, self.logger)

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
        new_item = test_gen(self.fake)
        new_item[required_param] = None
        posted_item_id = post_item(self.pool, new_item, self.logger)
        self.assertIsNone(posted_item_id)

    def _test_post_item_missing_param(self, param: str, test_gen: Callable[[Faker], dict], post_item: Callable[[Connection, dict, logging.Logger], int or None]):
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
                    'id', 'created_at', 'updated_at', 'price', 'rating', 'coord', 'amenities'])
        delete_keys(test_listing, ['price', 'rating', 'coord', 'amenities'])
        self.assertDictEqual(test_listing, fetched_listing)

    def create_fake_listing_with_host_id(self):
        test_user_id = self.test_user['id']
        new_host = create_fake_host(self.fake, test_user_id)
        new_host_id = post_host(self.pool, new_host, self.logger)

        return lambda faker: create_fake_listing(faker, new_host_id)

    def test_get_host(self):
        self._test_get_item(self.create_fake_listing_with_host_id(
        ), self.listing_equality_check, post_listing, get_listing)

    def test_get_host_missing_param(self):
        self._test_get_item_invalid_param(
            self.create_fake_listing_with_host_id(), post_listing, get_listing)

    def test_post_host(self):
        self._test_post_item(
            self.create_fake_listing_with_host_id(), post_listing, get_listing)

    def test_post_host_missing_required_param(self):
        self._test_post_item_missing_required_param(
            'host_id', self.create_fake_listing_with_host_id(), post_listing)

    def test_post_host_missing_param(self):
        self._test_post_item_missing_param(
            'bedrooms', self.create_fake_listing_with_host_id(), post_listing)

    def test_get_listings(self):
        args_dic = {
            'count': 11,
        }
        listings = self._test_get_items(
            self.create_fake_listing_with_host_id(),
            self.listing_equality_check,
            post_listing,
            get_listing,
            args_dic
        )

        listings_with_args = get_listing(self.pool, {
            'room_type': listings[0]['room_type'],
            'count': 10
        })
        self.assertGreaterEqual(len(listings_with_args), 1)

        found_item = next(
            item for item in listings_with_args if item["id"] == listings[0]["id"])
        self.assertIsNotNone(found_item)
        self.assertEqual(found_item['id'], listings[0]['id'])

class TestAnalyticsMethods(MethodTester):
    def test_best_listings_query(self):
        query_lst = [
            sql.SQL('WHERE best_listings.price < %(price)s')
        ]
        query_lst_args = {
            'price': 10000
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
        self.assertEqual(len(listings), 10)

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
        self.assertAlmostEqual(fetched_listing['rating'], Decimal(test_listing['rating']))
        self.assertEqual(fetched_listing['listing_id'], test_listing['listing_id'])
        self.assertEqual(fetched_listing['reviewer_id'], test_listing['reviewer_id'])
        self.assertEqual(fetched_listing['comments'], test_listing['comments'])


    def test_get_reviews(self):
        self._test_get_item(self.create_fake_review_with_user_id(), self.equality_check, post_review, get_reviews)

    def test_get_reviews_missing_param(self):
        self._test_get_item_invalid_param(self.create_fake_review_with_user_id(), post_review, get_reviews)

    def test_post_reviews(self):
        self._test_post_item(self.create_fake_review_with_user_id(), post_review, get_reviews)

    def test_post_reviews_missing_required_param(self):
        self._test_post_item_missing_required_param('listing_id', self.create_fake_review_with_user_id(), post_review)

if __name__ == '__main__':
    unittest.main()
