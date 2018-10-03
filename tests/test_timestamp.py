import datetime
import json
import unittest

import pytz
from test_app import BaseTestCase


class TestTimestampView(BaseTestCase, unittest.TestCase):
    def test_index(self):
        """Test that the description view for this api is running."""

        url = self.app.get('/timestamp')
        self.assertTrue(url.data)
        self.assertEqual(url.status_code, 200)


class TestTimestampApi(BaseTestCase, unittest.TestCase):
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
        self.assertEqual(response.json, json.dumps({'error': 'Invalid Date'}))


if __name__ == '__main__':
    unittest.main()
