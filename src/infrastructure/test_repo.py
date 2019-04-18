import unittest

from repository import Repository

class TestRepository(unittest.TestCase):

    def setUp(self):
        self.repo = Repository()

    def test_add(self):
        # TODO: test exceptions
        pass

    def test_get(self):
        # Assuming that database if filled at least once
        self.assertEquals(len(self.repo.get()), 5)

if __name__ == "__main__":
    unittest.main()