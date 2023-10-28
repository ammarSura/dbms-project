from decimal import Decimal
from typing import Callable
import unittest
from psycopg import Connection
from get_host import get_host
from get_listing import get_listing
from get_user import get_user
from post_host import post_host
from post_listing import post_listing
from post_user import post_user
from db_utils import create_pool
from faker import Faker
import logging

from test_utils import create_fake_host, create_fake_listing, create_fake_user, delete_keys

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

    def _test_get_item(self, test_gen: Callable[[Faker], dict], equality_check: Callable[[dict, dict], bool], post_item: Callable[[Connection, dict, logging.Logger], int or None], get_item: Callable[[Connection, dict], dict or None]):
        test_item = test_gen(self.fake)
        posted_item_id = post_item(self.pool, test_item, self.logger)

        fetched_item = get_item(self.pool, {
            'id': posted_item_id
        })
        equality_check(test_item, fetched_item)

    def _test_get_item_missing_param(self, get_item: Callable[[Connection, dict], dict or None]):
        fetched_item = get_item(self.pool, {
            'id': None
        })
        self.assertIsNone(fetched_item)

    def _test_post_item(self, test_gen: Callable[[Faker], dict], equality_check: Callable[[dict, dict], bool], post_item: Callable[[Connection, dict, logging.Logger], int or None], get_item: Callable[[Connection, dict], dict or None]):
        new_item = test_gen(self.fake)
        posted_item_id = post_item(self.pool, new_item, self.logger)
        self.assertIsNotNone(posted_item_id)
        fetched_user = get_item(self.pool, {
            'id': posted_item_id
        })
        self.assertIsNotNone(fetched_user)
        self.assertEqual(fetched_user['id'], posted_item_id)
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
        self._test_get_item(create_fake_user, self.user_equality_check, post_user, get_user)
    def test_get_user_missing_param(self):
        self._test_get_item_missing_param(get_user)
    def test_post_user(self):
        self._test_post_item(create_fake_user, self.user_equality_check, post_user, get_user)
    def test_post_item_missing_required_param(self):
        return self._test_post_item_missing_required_param('name', create_fake_user, post_user)
    def test_post_item_missing_param(self):
        return self._test_post_item_missing_param('picture_url', create_fake_user, post_user)

class TestHostMethods(MethodTester):
    def host_equality_check(self, test_host: dict, fetched_host: dict or None):
        self.assertIsNotNone(fetched_host)
        self.assertIsNotNone(fetched_host['created_at'])
        self.assertIsNotNone(fetched_host['updated_at'])
        acceptance_rate = fetched_host['acceptance_rate'], test_host['acceptance_rate']
        response_rate = fetched_host['response_rate'], test_host['response_rate']
        self.assertAlmostEqual(acceptance_rate[0], Decimal(acceptance_rate[1]))
        self.assertAlmostEqual(response_rate[0], Decimal(response_rate[1]))
        del fetched_host['id'], fetched_host['created_at'], fetched_host['updated_at']
        del fetched_host['acceptance_rate'], fetched_host['response_rate']
        del test_host['response_rate'], test_host['acceptance_rate']

        self.assertDictEqual(test_host, fetched_host)

    def create_fake_host_with_user_id(self):
        test_user_id = self.test_user['id']
        return lambda faker: create_fake_host(faker, test_user_id)

    def test_get_host(self):
        self._test_get_item(self.create_fake_host_with_user_id(), self.host_equality_check, post_host, get_host)
    def test_get_host_missing_param(self):
        self._test_get_item_missing_param(get_host)
    def test_post_host(self):
        self._test_post_item(self.create_fake_host_with_user_id(), self.host_equality_check, post_host, get_host)
    def test_post_host_missing_required_param(self):
        return self._test_post_item_missing_required_param('user_id', self.create_fake_host_with_user_id(), post_host)
    def test_post_host_missing_param(self):
        return self._test_post_item_missing_param('about', self.create_fake_host_with_user_id(), post_host)

class TestListingMethods(MethodTester):
    def listing_equality_check(self, test_listing: dict, fetched_listing: dict or None):
        self.maxDiff = None
        self.assertIsNotNone(fetched_listing)
        self.assertIsNotNone(fetched_listing['created_at'])
        self.assertIsNotNone(fetched_listing['updated_at'])
        self.assertAlmostEqual(fetched_listing['price'], Decimal(test_listing['price']))
        self.assertAlmostEqual(fetched_listing['review_rating'], Decimal(test_listing['review_rating']))
        self.assertListEqual(test_listing['amenities'], fetched_listing['amenities'])
        delete_keys(fetched_listing, ['id', 'created_at', 'updated_at', 'price', 'review_rating', 'coors'])
        delete_keys(test_listing, ['price', 'review_rating', 'coors'])

        self.assertDictEqual(test_listing, fetched_listing)

    def create_fake_listing_with_host_id(self):
        test_user_id = self.test_user['id']
        new_host = create_fake_host(self.fake, test_user_id)
        new_host_id = post_host(self.pool, new_host, self.logger)

        return lambda faker: create_fake_listing(faker, test_user_id, new_host_id)
    def test_get_host(self):
        return self._test_get_item(self.create_fake_listing_with_host_id(), self.listing_equality_check, post_listing, get_listing)
    def test_get_host_missing_param(self):
        return self._test_get_item_missing_param(get_listing)
    def test_post_host(self):
        return self._test_post_item(self.create_fake_listing_with_host_id(), self.listing_equality_check, post_listing, get_listing)
    def test_post_host_missing_required_param(self):
        return self._test_post_item_missing_required_param('host_id', self.create_fake_listing_with_host_id(), post_listing)
    def test_post_host_missing_param(self):
        return self._test_post_item_missing_param('bedrooms', self.create_fake_listing_with_host_id(), post_listing)

if __name__ == '__main__':
    unittest.main()

