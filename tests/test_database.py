import kollokvie_chat.database as database
import kollokvie_chat.models as models

import datetime
import unittest


def create_test_user():
    user = models.User()
    user.name = 'Test User'
    user.email = 'test@example.org'
    user.avatar = 'avatar'
    user.status = 'status'
    user.language = 'language'
    user.password = 'password'
    return user


def create_test_message():
    msg = models.Message()
    msg.date = datetime.datetime(2007, 12, 5, hour=12, minute=30, second=0)
    msg.content = 'some content'
    return msg


def create_test_room():
    room = models.Room()
    room.name = 'Some room'
    room.slug = 'Some room'
    room.topic = 'topic'
    room.date_created = datetime.datetime(2005, 4, 5, hour=12, minute=30,
                                          second=0)
    room.deleted = False
    room.language = 'nb_no'
    return room


def create_test_attachment():
    attachment = models.Attachment()
    attachment.data = 'data'
    attachment.size = 5000
    attachment.mime_type = 'text/plain'
    return attachment


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
