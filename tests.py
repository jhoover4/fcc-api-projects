import unittest


from app import app
import models

models.initialize()


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


class AppTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_index(self):
        url = self.app.get('/')
        self.assertTrue(url.data)
        self.assertEqual(url.status_code, 200)


if __name__ == '__main__':
    unittest.main()
