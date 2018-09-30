import datetime
import json
import unittest

import pytz

import models
from app import app

MODELS = [models.Urls, models.ImageSearches]


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        """Initialize models, create test user, and setup test app."""

        app.testing = True
        self.app = app.test_client()

        models.initialize()

    def tearDown(self):
        """Delete tables in peewee test database."""

        models.DATABASE.drop_tables(MODELS)
        models.DATABASE.close()


class UrlTests(unittest.TestCase):

    def setUp(self):
        self.original_url = 'wordpress.com'

        self.test_url = models.Urls.create(
            original_url=self.original_url,
        )

    def tearDown(self):
        try:
            self.test_url.delete_instance()
        except:
            pass

    def test_check_table(self):
        assert models.Urls.table_exists()

    def test_original_url_field(self):
        url = models.Urls.get(orginal_url=self.original_url)
        self.assertEqual(self.original_url, url.orginal_url)

    def test_url_repeat_short(self):
        with self.assertRaises(ValueError):
            models.Urls.create(
                original_url='www.twitter.com',
                short_url=self.test_url.short_url
            )

    def test_delete_url(self):
        models.Task.get(original_url=self.original_url).delete_instance()
        with self.assertRaises(Exception):
            models.Task.get(original_url=self.original_url).delete_instance()


class ImageSearchTests(unittest.TestCase):

    def setUp(self):
        self.img_search_query = 'Dogs'

        self.test_img_search = models.Urls.create(
            search_query=self.img_search_query,
        )

    def tearDown(self):
        try:
            self.test_img_search.delete_instance()
        except:
            pass

    def test_check_image_searches_table(self):
        assert models.ImageSearches.table_exists()

    def test_search_query_field(self):
        query = models.ImageSearches.get(search_query=self.img_search_query)
        self.assertEqual(self.img_search_query, query.search_query)

    def test_delete_query(self):
        models.Task.get(search_query=self.img_search_query).delete_instance()
        with self.assertRaises(Exception):
            models.Task.get(search_query=self.img_search_query).delete_instance()


class AppTests(BaseTestCase):
    def test_index(self):
        url = self.app.get('/')
        self.assertTrue(url.data)
        self.assertEqual(url.status_code, 200)


class TestTimestampApi(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.date = datetime.datetime.now()
        gmt = pytz.timezone('GMT')
        local_date = gmt.localize(self.date)

        self.returned_data = {
            'unix': local_date.timestamp(),
            'utc': datetime.datetime.strftime(local_date, '%a, %d %b %Y %B %X %Z')
        }

    def test_get_no_date(self):
        """Test timestamp get method with no arguments passed."""

        response = self.app.get("/api/timestamp")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['utc'], self.returned_data['utc'])

    def test_get_with_unix(self):
        """Test timestamp get method using unix parameter."""

        date = self.date.timestamp()
        response = self.app.get(f"/api/timestamp/{date}")
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['unix'], date)
        self.assertEqual(response_data['utc'], self.returned_data['utc'])

    def test_get_with_utc(self):
        """Test timestamp get method using utc parameter."""

        date = datetime.datetime.strftime(self.date, '%Y-%m-%d')
        response = self.app.get(f"/api/timestamp/{date}")

        response_data = json.loads(response.data)
        response_data_utc = datetime.datetime.strptime(response_data['utc'], '%a, %d %b %Y %B %X %Z')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response_data['unix'])[:4], str(self.returned_data['unix'])[:4])
        self.assertEqual(response_data_utc.day, self.date.day)

    def test_get_bad_date(self):
        """Test timestamp get method with incorrect date format."""

        response = self.app.get("/api/timestamp/07-07-0000")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), json.dumps({'error': 'Invalid Date'}))


if __name__ == '__main__':
    unittest.main()
