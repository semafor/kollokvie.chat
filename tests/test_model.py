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
        models.db = self.db

    def tearDown(self):
        self.db.cleanup()
        del self.db


class TestBase(unittest.TestCase):

    def test_id(self):
        b = models.Base()
        self.assertEqual(b.get_id(), -1)

    def test_base_create(self):
        b = models.Base()
        with self.assertRaises(NotImplementedError):
            b.save()

    def test_base_update(self):
        b = models.Base()
        b._reified = True
        with self.assertRaises(NotImplementedError):
            b.save()


class TestUsers(BaseTestCase):

    def test_create_user_from_row(self):
        row = {
            'name': 'Test Person',
            'email': 'test@example.org',
            'avatar': 'avatar',
            'status': 'status',
            'language': 'language',
            'password': 'password',
        }
        user = models.User.from_row(row)

        self.assertEqual(user.name, row['name'])
        self.assertEqual(user.email, row['email'])
        self.assertEqual(user.avatar, row['avatar'])
        self.assertEqual(user.status, row['status'])
        self.assertEqual(user.language, row['language'])
        self.assertEqual(user.password, row['password'])

    def test_create_password(self):
        user = models.User()
        user.set_password('hunter2', {'hashing_rounds': 2000})
        self.assertIsNotNone(user.password)

    def test_compare_password(self):
        user = models.User()
        user.set_password('hunter2', {'hashing_rounds': 2000})
        self.assertTrue(user.compare_password('hunter2'))
        self.assertFalse(user.compare_password('wrong'))

    def test_create_user(self):
        user = create_test_user()
        user.save()

        dbuser = models.User.get(user.get_id())
        self.assertEqual(user.name, dbuser.name)
        self.assertEqual(user.email, dbuser.email)
        self.assertEqual(user.avatar, dbuser.avatar)
        self.assertEqual(user.status, dbuser.status)
        self.assertEqual(user.language, dbuser.language)
        self.assertEqual(user.password, dbuser.password)

    def test_update_user(self):
        user = create_test_user()
        user.save()
        user.name = 'new name'
        with self.assertRaises(NotImplementedError):
            user.save()

    def test_get_all_users(self):
        user1 = create_test_user()
        user1.email = 'aaa@example.org'
        user1.save()

        user2 = create_test_user()
        user2.email = 'bbb@example.org'
        user2.save()

        users = models.User.get_all(order_by='email', order='ASC')
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0].email, user1.email)
        self.assertEqual(users[1].email, user2.email)

    def test_user_does_not_see_room_not_visited(self):
        user = create_test_user()
        user.save()
        room = create_test_room()
        room.save()

        self.assertEqual([], user.get_rooms())

    def test_user_sees_rooms_visited(self):
        user = create_test_user()
        user.save()
        room = create_test_room()
        room.save()
        room.add(user)
        rooms = user.get_rooms()
        self.assertEqual(1, len(rooms))
        self.assertEqual(rooms[0].name, room.name)

    def test_user_in_room(self):
        user = create_test_user()
        user.save()
        room1 = create_test_room()
        room1.save()
        room1.add(user)
        room2 = create_test_room()
        room2.name = "foo"
        room2.slug = room2.name
        room2.save()

        self.assertTrue(user.in_room(room1))
        self.assertFalse(user.in_room(room2))

    def test_user_joined_room_when(self):
        user = create_test_user()
        user.save()
        room1 = create_test_room()
        room1.save()

        room2 = create_test_room()
        room2.name = "foo"
        room2.slug = room2.name
        room2.save()

        room1.add(user)
        room2.add(user)

        self.assertEqual(user.get_recent_room().name, room2.name)


class TestMessages(BaseTestCase):

    def test_create_message_from_row(self):
        row = {
            'mid': 0,
            'date': 0,
            'content': 'some content'
        }
        message = models.Message.from_row(row)

        self.assertEqual(message.get_id(), row['mid'])
        self.assertEqual(message.date, row['date'])
        self.assertEqual(message.content, row['content'])

    def test_create_message(self):
        message = create_test_message()
        message.save()
        res = self.db.executeSelect('SELECT * FROM messages')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['content'], message.content)

    def test_link_user_message_without_creating_it_first(self):
        user = create_test_user()
        user.save()
        message = create_test_message()
        with self.assertRaises(sqlite3.DatabaseError):
            user.add(message)

    def test_link_user_message(self):
        user = create_test_user()
        user.save()
        message = create_test_message()
        message.save()

        user.add(message)

        res = self.db.executeSelect('SELECT * FROM user_messages')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['owner_id'], user.get_id())
        self.assertEqual(int(res[0]['message_id']), message.get_id())

    def test_message_owner(self):
        user = create_test_user()
        user.save()
        message = create_test_message()
        message.save()

        user.add(message)

        owner = message.get_owner()
        self.assertEqual(user.get_id(), owner.get_id())

    def test_long_redable_date(self):
        message = create_test_message()
        message.save()

        message1 = models.Message.get(message.get_id())
        self.assertTrue(type(message1.date) is datetime.datetime)
        self.assertEqual(message1.human_readable_date(),
                         'Wed 3. Dec, 2007 12:30:00')

    def test_short_redable_date(self):
        message = create_test_message()
        now = datetime.datetime.now()
        message.date = datetime.datetime(
            now.year, now.month, now.day, hour=12, minute=30, second=0)

        message.save()

        message1 = models.Message.get(message.get_id())
        self.assertTrue(type(message1.date) is datetime.datetime)
        self.assertEqual(message1.human_readable_date(),
                         '12:30')


class TestRooms(BaseTestCase):

    def test_slug(self):
        room = models.Room()
        room.name = ''
        room.slug = 'foo bar baz'
        room.topic = 'topic'
        room.date_created = 0
        room.deleted = 0
        room.language = 'language'

        self.assertEqual(room.to_row()['slug'], 'foo-bar-baz')

    def test_create_room(self):
        room = create_test_room()
        room.save()

        res = self.db.executeSelect('SELECT * FROM rooms')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['name'], room.name)

    def test_link_message_without_creating_it_first(self):
        room = create_test_room()
        room.save()
        message = create_test_message()

        with self.assertRaises(sqlite3.DatabaseError):
            room.add(message)

    def test_link_room_without_creating_it_first(self):
        room = create_test_room()
        message = create_test_message()
        message.save()
        with self.assertRaises(sqlite3.DatabaseError):
            room.add(message)

    def test_link_room_message(self):
        room = create_test_room()
        room.save()
        message = create_test_message()
        message.save()
        room.add(message)

        res = self.db.executeSelect('SELECT * FROM room_messages')
        self.assertEqual(len(res), 1)
        self.assertEqual(int(res[0]['room_id']), room.get_id())
        self.assertEqual(int(res[0]['message_id']), message.get_id())

    def test_get_single(self):
        room = create_test_room()
        room.save()

        dbroom = models.Room.get(room.get_id())
        self.assertEqual(room.get_id(), dbroom.get_id())
        self.assertEqual(room.name, dbroom.name)

    def test_no_two_equal_slugs(self):
        room = create_test_room()
        room.save()
        room2 = create_test_room()
        with self.assertRaises(sqlite3.IntegrityError):
            room2.save()

    def test_join_user(self):
        user = create_test_user()
        user.save()
        room = create_test_room()
        room.save()
        room.add(user)
        res = self.db.executeSelect('SELECT * FROM user_rooms')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['user_id'], user.get_id())
        self.assertEqual(int(res[0]['room_id']), room.get_id())

    def test_part_user(self):
        user = create_test_user()
        user.save()
        room = create_test_room()
        room.save()
        room.add(user)
        room.remove(user)

        res = self.db.executeSelect('SELECT * FROM user_rooms')
        self.assertEqual(len(res), 0)

    def test_get_messages(self):
        room = create_test_room()
        room.save()

        message1 = create_test_message()
        message1.content = 'first'
        message1.date = datetime.datetime(2012, 1, 1)
        message1.save()
        message2 = create_test_message()
        message2.date = datetime.datetime(2015, 1, 1)
        message2.content = 'second'
        message2.save()
        room.add(message1)
        room.add(message2)

        messages = room.get_messages()
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].content, 'first')
        self.assertEqual(messages[1].content, 'second')

        messages = room.get_messages(order='DESC')
        self.assertEqual(messages[0].content, 'second')
        self.assertEqual(messages[1].content, 'first')

    # def test_update_room(self):
    #     pass

    def test_get_messages_from(self):
        room = create_test_room()
        room.save()

        message1 = create_test_message()
        message1.content = 'first'
        message1.save()
        message2 = create_test_message()
        message2.content = 'second'
        message2.save()
        room.add(message1)
        room.add(message2)

        messages = room.get_messages_from(1)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].content, 'second')

    def test_get_by_name(self):
        room = create_test_room()
        room.save()

        r = models.Room.get_by_name(room.name)
        self.assertIsNotNone(r)
        self.assertEqual(room.name, r.name)

        self.assertIsNone(models.Room.get_by_name("not exist"))

    def test_contains_user(self):
        room = create_test_room()
        room.save()

        user1 = create_test_user()
        user1.email = 'aaa@example.org'
        user1.save()
        room.add(user1)

        user2 = create_test_user()
        user2.email = 'bbb@example.org'
        user2.save()

        self.assertTrue(room.contains_user(user1))
        self.assertFalse(room.contains_user(user2))

    def test_get_all_except_some(self):
        room1 = create_test_room()
        room1.save()
        room2 = create_test_room()
        room2.name = "foo"
        room2.slug = room2.name
        room2.save()

        get_all = models.Room.get_all(order_by='rid', blacklist=[room1])
        self.assertEqual(1, len(get_all))
        self.assertEqual(room2, get_all[0])


class TestAttachments(BaseTestCase):

    def test_create_attachment(self):
        att = create_test_attachment()
        att.save()
        res = self.db.executeSelect('SELECT * FROM attachments')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['data'], att.data)

    def test_link_attachment_without_creating_it_first(self):
        att = create_test_attachment()
        message = create_test_message()
        message.save()

        with self.assertRaises(sqlite3.DatabaseError):
            message.add(att)

    def test_link_attachment_without_creating_a_message_first(self):
        att = create_test_attachment()
        att.save()
        message = create_test_message()
        with self.assertRaises(sqlite3.DatabaseError):
            message.add(att)

    def test_link_attachment_message(self):
        message = create_test_message()
        message.save()
        att = create_test_attachment()
        att.save()

        message.add(att)
        res = self.db.executeSelect('SELECT * FROM messages_attachments')
        self.assertEqual(len(res), 1)
        self.assertEqual(int(res[0]['message_id']), message.get_id())
        self.assertEqual(int(res[0]['attachment_id']), att.get_id())


if __name__ == '__main__':
    unittest.main()
