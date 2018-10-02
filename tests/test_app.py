import unittest

import models
from app import app

MODELS = [models.Url, models.ImageSearches, models.ExerciseUser, models.Exercise]


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


class AppTests(BaseTestCase):
    def test_index(self):
        url = self.app.get('/')
        self.assertTrue(url.data)
        self.assertEqual(url.status_code, 200)


if __name__ == '__main__':
    unittest.main()
