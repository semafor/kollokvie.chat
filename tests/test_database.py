import kollokvie_chat.database as database
import kollokvie_chat.models as models

import datetime
import sqlite3
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


# class TestUsers(BaseTestCase):

#     def test_add_user(self):
#         user = create_test_user()
#         self.db.add_user(user)
#         dbuser = self.db.get_user('test@example.org')

#         self.assertEqual(user.name, dbuser.name)
#         self.assertEqual(user.email, dbuser.email)
#         self.assertEqual(user.avatar, dbuser.avatar)
#         self.assertEqual(user.status, dbuser.status)
#         self.assertEqual(user.language, dbuser.language)
#         self.assertEqual(user.password, dbuser.password)

#     def test_change_user(self):
#         user = create_test_user()
#         self.db.add_user(user)
#         user.name = 'Something else'
#         self.db.add_user(user)
#         res = self.db.executeSelect('SELECT * FROM users')

#         self.assertEqual(len(res), 1)
#         self.assertEqual(res[0]['name'], user.name)

#     def test_user_joins_room(self):
#         room = create_test_room()
#         user = create_test_user()
#         self.db.add_user(user)
#         self.db.add_room(room)

#         self.db.link_user_room(user, room)

#         res = self.db.executeSelect('SELECT * FROM user_rooms')
#         self.assertEqual(len(res), 1)
#         self.assertEqual(res[0]['user_id'], user.get_id())
#         self.assertEqual(int(res[0]['room_id']), room.get_id())

#     def test_user_joins_room_twice(self):
#         room = create_test_room()
#         user = create_test_user()
#         self.db.add_user(user)
#         self.db.add_room(room)

#         self.db.link_user_room(user, room)
#         self.db.link_user_room(user, room)

#         res = self.db.executeSelect('SELECT * FROM user_rooms')
#         self.assertEqual(len(res), 1)

#     def test_user_parts_room(self):
#         room = create_test_room()
#         user = create_test_user()
#         self.db.add_user(user)
#         self.db.add_room(room)

#         self.db.link_user_room(user, room)
#         self.db.unlink_user_room(user, room)

#         res = self.db.executeSelect('SELECT * FROM user_rooms')
#         self.assertEqual(len(res), 0)

#     def test_room_messages(self):
#         room = create_test_room()
#         self.db.add_room(room)
#         msg = create_test_message()
#         msg.content = 'a'
#         self.db.add_message(msg)
#         mid = msg.get_id()
#         msg.content = 'b'
#         self.db.add_message(msg)
#         msg.content = 'c'
#         self.db.add_message(msg)

#         a = self.db.get_single(models.Message, mid)
#         print(a.get_id())
#         self.db.link_room_message(room, a)
#         room_msg = self.db.get_messages(room)
#         self.assertEqual(1, len(room_msg))
#         self.assertEqual(a.content, room_msg[0].content)


# # class TestMessages(BaseTestCase):

# #     def setUp(self):
# #         super(TestMessages, self).setUp()
# #         self.user = create_test_user()
# #         self.msg = create_test_message()

# #     def test_add_message(self):
# #         self.db.add_message(self.msg)
# #         res = self.db.executeSelect('SELECT * FROM messages')
# #         self.assertEqual(len(res), 1)
# #         self.assertEqual(res[0]['content'], self.msg.content)

# #     def test_link_user_message_without_creating_it_first(self):
# #         with self.assertRaises(sqlite3.DatabaseError):
# #             self.db.link_user_message(self.user, self.msg)

# #     def test_link_user_message(self):
# #         self.db.add_message(self.msg)
# #         self.db.link_user_message(self.user, self.msg)

# #         res = self.db.executeSelect('SELECT * FROM user_messages')
# #         self.assertEqual(len(res), 1)
# #         self.assertEqual(res[0]['owner_id'], self.user.get_id())
# #         self.assertEqual(int(res[0]['message_id']), self.msg.get_id())

# #     def test_message_owner(self):
# #         self.db.add_message(self.msg)
# #         self.db.add_user(self.user)
# #         self.db.link_user_message(self.user, self.msg)

# #         owner = self.db.get_message_owner(self.msg)
# #         self.assertEqual(self.user.get_id(), owner.get_id())


# class TestRooms(BaseTestCase):

#     def setUp(self):
#         super(TestRooms, self).setUp()
#         self.user = create_test_user()
#         self.msg = create_test_message()
#         self.room = create_test_room()

#     def test_add_room(self):
#         self.db.add_room(self.room)
#         res = self.db.executeSelect('SELECT * FROM rooms')
#         self.assertEqual(len(res), 1)
#         self.assertEqual(res[0]['name'], self.room.name)

#     def test_link_message_without_creating_it_first(self):
#         self.db.add_room(self.room)
#         with self.assertRaises(sqlite3.DatabaseError):
#             self.db.link_room_message(self.room, self.msg)

#     def test_link_room_without_creating_it_first(self):
#         self.db.add_message(self.msg)
#         with self.assertRaises(sqlite3.DatabaseError):
#             self.db.link_room_message(self.room, self.msg)

#     def test_link_room_message(self):
#         self.db.add_room(self.room)
#         self.db.add_message(self.msg)
#         self.db.link_room_message(self.room, self.msg)

#         res = self.db.executeSelect('SELECT * FROM room_messages')
#         self.assertEqual(len(res), 1)
#         self.assertEqual(int(res[0]['room_id']), self.room.get_id())
#         self.assertEqual(int(res[0]['message_id']), self.msg.get_id())

#     def test_get_single(self):
#         self.db.add_room(self.room)
#         room = self.db.get_single(models.Room, self.room.get_id())
#         self.assertEqual(room.get_id(), self.room.get_id())
#         self.assertEqual(room.name, self.room.name)

#     def test_no_two_equal_slugs(self):
#         self.db.add_room(self.room)
#         with self.assertRaises(sqlite3.IntegrityError):
#             self.db.add_room(self.room)

#     def test_update_room(self):
#         pass


# class TestAttachments(BaseTestCase):

#     def setUp(self):
#         super(TestAttachments, self).setUp()
#         self.msg = create_test_message()
#         self.attachment = create_test_attachment()

#     def test_add_attachment(self):
#         self.db.add_attachment(self.attachment)
#         res = self.db.executeSelect('SELECT * FROM attachments')
#         self.assertEqual(len(res), 1)
#         self.assertEqual(res[0]['data'], self.attachment.data)

#     def test_link_attachment_creating_it_first(self):
#         self.db.add_message(self.msg)
#         with self.assertRaises(sqlite3.DatabaseError):
#             self.db.link_attachment_message(self.msg, self.attachment)

#     def test_link_attachment_creating_a_message_first(self):
#         self.db.add_attachment(self.attachment)
#         with self.assertRaises(sqlite3.DatabaseError):
#             self.db.link_attachment_message(self.msg, self.attachment)

#     def test_link_attachment_message(self):
#         self.db.add_attachment(self.attachment)
#         self.db.add_message(self.msg)
#         self.db.link_attachment_message(self.msg, self.attachment)

#     def test_wrong_arg_order_one(self):
#         with self.assertRaises(TypeError):
#             self.db.link_attachment_message(self.attachment, self.msg)

#     def test_wrong_arg_order_two(self):
#         with self.assertRaises(TypeError):
#             self.db.link_attachment_message(self.msg, self.msg)


if __name__ == '__main__':
    unittest.main()
