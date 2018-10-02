import json
import unittest

from test_app import BaseTestCase

import models
from resources.url_shortener import valid_url


class UrlCreationTests(BaseTestCase, unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.headers = {
            'content-type': 'application/json'
        }
        self.post_data = {
            'url': 'https://www.facebook.com'
        }

    def test_check_table(self):
        assert models.Url.table_exists()

    def test_url_creation_post(self):
        """Test url post is created successfully."""

        response = self.app.post('/api/shorturl/new', headers=self.headers, data=json.dumps(self.post_data))
        self.assertEqual(response.status_code, 201)

        new_url = models.Url.get()

        self.assertEqual(json.loads(response.data), {'original_url': new_url.original_url, 'short_url': new_url.id})

    def test_url_creation_post_existing(self):
        """Test that existing url is found when info is posted."""

        new_url = models.Url.create(original_url='https://www.facebook.com')
        response = self.app.post('/api/shorturl/new', headers=self.headers, data=json.dumps(self.post_data))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), {'original_url': new_url.original_url, 'short_url': new_url.id})

    def test_valid_url(self):
        """Test that the valid_url function works correctly."""

        url = 'www.google.com'

        self.assertEqual(valid_url(url), 'https://' + url)

    def test_valid_url_bad_formatting(self):
        """Test that the valid_url function catches poorly formatted urls."""

        url = 'https://aasdf'

        with self.assertRaises(ValueError):
            valid_url(url)

    def test_valid_url_bad_route(self):
        """Test that the valid_url function catches urls that are offline."""

        url = 'http://www.a.com'

        with self.assertRaises(ValueError):
            valid_url(url)


class UrlRedirectTests(BaseTestCase, unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.test_url = models.Url.create(
            original_url='https://www.google.com',
        )

    def test_redirect(self):
        """Test that the redirect using the original_url value is working properly."""

        response = self.app.get("/api/shorturl/1")
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.test_url.original_url, str(response.data))

    def test_redirect_bad_input(self):
        """Test that the redirect throws 404 with bad input."""

        response = self.app.get("/api/shorturl/3")
        self.assertEqual(response.status_code, 404)
