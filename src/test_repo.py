import unittest

from infrastructure.repository import Repository
from infrastructure.parser import Parser
from infrastructure.errors import BadArgumentError


class TestRepository(unittest.TestCase):

    def setUp(self):
        with open('resources/example.html', 'r') as f_in:
            html = f_in.read()
        self.repo = Repository()
        self.repo.add_many(Parser.parse_news(html))

    def test_add(self):
        # TODO: test exceptions
        pass

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


if __name__ == "__main__":
    unittest.main()