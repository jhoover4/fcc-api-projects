import unittest

from app import app
from resources.request_parser import RequestParser


class TestRequestParserApi(unittest.TestCase):
    def setUp(self):
        """Create test user, and setup test app."""

        app.testing = True
        self.app = app.test_client()

    def test_route(self):
        response = self.app.get("/api/whoami")

        self.assertEqual(response.status_code, 200)

    def test_header_info(self):
        response = self.app.get("/api/whoami")
        headers = {
            'ipaddress': '127.0.0.1',
            'language': '',
            'software': 'werkzeug/0.14.1'
        }

        self.assertEqual(response.json, headers)

    def test_empty_strings(self):
        value = RequestParser.empty_string_if_none(None)

        self.assertEqual(value, "")
