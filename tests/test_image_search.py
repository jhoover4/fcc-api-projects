import datetime
import json
import unittest

from test_app import BaseTestCase

import models


class TestImageSearchView(BaseTestCase, unittest.TestCase):
    def test_check_table(self):
        assert models.ImageSearch.table_exists()

    def test_index(self):
        """Test that the description view for this api is running."""

        url = self.app.get('/image-search')
        self.assertTrue(url.data)
        self.assertEqual(url.status_code, 200)


class TestImageSearchApi(BaseTestCase, unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.search_record = models.ImageSearch.create(search_query='cats')

    def test_new_search(self):
        """Test search is performed correctly and returns json data."""

        response = self.app.get('/api/image-search/cats')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json[0]['displayLink'])

    def test_new_search_offset(self):
        """Test search is performed correctly with offset parameter"""

        response = self.app.get('/api/image-search/cats')
        offset_response = self.app.get('/api/image-search/cats', query_string={'offset': 15})

        self.assertEqual(offset_response.status_code, 200)
        self.assertNotEqual(offset_response.json[0]['formattedUrl'], response.json[0]['formattedUrl'])

    def test_new_query_in_args(self):
        """Test search is performed with query in parameters."""

        response = self.app.get('/api/image-search', query_string={'query': 'cats'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json[0]['displayLink'])

    def test_new_query_in_args_empty(self):
        """Test error is thrown if query not in url at all."""

        response = self.app.get('/api/image-search')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.data), {
            'message': 'Query is required.'
        })

    def test_recent_searches(self):
        """Test all searches are returned on GET."""

        response = self.app.get('/api/image-search/recent')

        expected_data = [{
            'query': self.search_record.search_query,
            'when': datetime.datetime.strftime(self.search_record.created_at, '%a, %d %b %Y %X -0000')
        }]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), expected_data)
