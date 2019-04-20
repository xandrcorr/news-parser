import unittest
import time

from pymongo.errors import DuplicateKeyError

from infrastructure.repository import Repository
from infrastructure.parser import Parser
from infrastructure.errors import BadArgumentError


class TestRepository(unittest.TestCase):

    def setUp(self):

        with open('resources/example.html', 'r') as f_in:
            html = f_in.read()
        self.repo = Repository(database="test_db")
        self.repo.add_many(Parser.parse_news(html))

    def test_add(self):
        good = [
            {'title': 'Title1', 'url': 'http://example.com/1', 'created': time.time()},
            {'title': 'Title2', 'url': 'http://example.com/2', 'created': time.time()}
        ]
        self.assertEqual(self.repo.add_many(good), 2)
        self.assertEqual(self.repo.add_many([]), 0)
        with self.assertRaises(DuplicateKeyError):
            self.repo.add(good[0])

    def test_get(self):
        # Assuming that database if filled at least once
        self.assertEquals(len(self.repo.get()), 5)
        self.assertEqual(len(self.repo.get(limit=20)), 20)
        self.assertEqual(len(self.repo.get(limit=20, offset=5)), 20)
        with self.assertRaises(BadArgumentError):
            self.repo.get(limit=900)
        with self.assertRaises(BadArgumentError):
            self.repo.get(offset=900)
        with self.assertRaises(BadArgumentError):
            self.repo.get(sort_order="")
        with self.assertRaises(BadArgumentError):
            self.repo.get(sort_key="")

    def tearDown(self):
        self.repo.clean_db()

if __name__ == "__main__":
    unittest.main()