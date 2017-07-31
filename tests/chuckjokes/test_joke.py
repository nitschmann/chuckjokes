import unittest

from chuckjokes import Joke
from chuckjokes.db.client import DbClient
from chuckjokes.db.exceptions import ValuesAreNotUniqueException

class TestJoke(unittest.TestCase):
    def setUp(self):
        DbClient().reconnect()

    def tearDown(self):
        DbClient().close_connection()

    def test_class_definitions(self):
        self.assertEqual(Joke.__table__, "jokes")

    def test_settable_attributes(self):
        expeted_list = ["id", "api_id", "value", "categories", "created_at", "updated_at"]

        self.assertEqual(Joke.settable_attributes(), expeted_list)
        self.assertEqual(Joke().settable_attributes(), expeted_list)

    def test_columns(self):
        expeted_list = ["api_id", "value"]
        self.assertEqual(Joke().columns(), expeted_list)

    def test_init_with_unknown_attribute(self):
        with self.assertRaises(AttributeError) as joke:
            Joke(foo="bar")

        self.assertEqual("invalid attributes passed", str(joke.exception))

    def test_all(self):
        joke = Joke(value="new value", api_id="123")
        joke.save()

        ids = list(map((lambda j: j.id), Joke.all()))

        self.assertIn(joke.id, ids)

    def test_init_with_known_attributes(self):
        api_id = "api_id"
        value = "Chuck norris never needs tests, tests need Chuck Norris"

        joke = Joke(api_id=api_id, value=value)

        self.assertEqual(joke.api_id, api_id)
        self.assertEqual(joke.value, value)
        self.assertIsNone(joke.id)
        self.assertIsNone(joke.created_at)
        self.assertIsNone(joke.updated_at)

    def test_find(self):
        joke = Joke(value="new value", api_id="123")
        joke.save()
        find_result = Joke.find(joke.id)

        self.assertIsNotNone(find_result)
        self.assertEqual(find_result.id, joke.id)

    def test_find_by(self):
        api_id = "123-random-id"
        Joke(api_id=api_id, value="Sample joke").save()

        find_result = Joke.find_by("api_id", api_id)

        self.assertIsNotNone(find_result)
        self.assertEqual(find_result.api_id, api_id)

    def test_is_unique(self):
        api_id = "123-random-id"
        Joke(api_id=api_id, value="Sample joke").save()
        new_joke = Joke(api_id=api_id, value="Sample joke")

        self.assertFalse(new_joke.is_unique())

    def test_find_by_with_unknown_column(self):
        with self.assertRaises(NameError) as joke:
            Joke.find_by(column="foo", value="bar")

    def test_save_not_unqiue(self):
        api_id = "123-random-id"
        expected_error_message = "One or more attributes of ['api_id'] are already taken"
        Joke(api_id=api_id, value="Sample joke").save()

        with self.assertRaises(ValuesAreNotUniqueException) as joke:
            Joke(api_id=api_id, value="Sample joke").save()

        self.assertEqual(str(joke.exception), expected_error_message)

    def test_save(self):
        joke = Joke(value="new value", api_id="123")

        self.assertTrue(joke.save())
        self.assertEqual(1, joke.id)

    def test_update(self):
        joke = Joke(value="new value", api_id="123")
        joke.save()

        updated_value = "another value"
        joke.value = updated_value

        self.assertTrue(joke.save())

        joke = Joke.find(joke.id)
        self.assertEqual(joke.value, updated_value)
