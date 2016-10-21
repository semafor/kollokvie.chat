import kollokvie_chat.database as database
import kollokvie_chat.models as models

import unittest


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.db = database.Database(':memory:')
        self.db.initialize()

    def tearDown(self):
        self.db.cleanup()
        del self.db


class TestNoDatabase(unittest.TestCase):

    def test_initialization(self):
        try:
            db = database.Database(':memory:')
            db.initialize()
        except Exception:
            self.fail('initialize() raised unexpectedly!')


if __name__ == '__main__':
    unittest.main()
