import unittest

from chuckjokes import Category, Joke
from chuckjokes.db.client import DbClient

class TestCategory(unittest.TestCase):
    def setUp(self):
        DbClient().reconnect()

    def tearDown(self):
        DbClient().close_connection()

    def test_categories(self):
        category = "sport"
        joke = Joke(api_id="api_id", value="value", categories=[category])
        joke.save()

        jokes = Category.find_by("name", category).jokes()

        self.assertEqual(len(jokes), 1)
        self.assertEqual(jokes[0].id, joke.id)

