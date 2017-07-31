import unittest

from chuckjokes.db.client import DbClient

class TestEntity(unittest.TestCase):
    def test_is_singleton(self):
        c1 = DbClient()
        c2 = DbClient()

        self.assertEqual(id(c1), id(c2))
        self.assertEqual(id(c1.connection), id(c2.connection))

    def test_close_connection_and_reconnect(self):
        c = DbClient()
        prev_id = id(c.connection)
        c.close_connection()
        c.reconnect()

        self.assertNotEqual(prev_id, id(c.connection))
