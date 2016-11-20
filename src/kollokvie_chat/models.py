import sqlite3
import datetime

from passlib.hash import sha256_crypt as hasher
from slugify import slugify

db = None


class Base(object):

    SQL_UPDATE = None
    SQL_INSERT = None
    SQL_GET = None
    SQL_GET_ALL = None

    def __init__(self):
        self.id = -1
        self._reified = False

    def get_id(self):
        return self.id

    def save(self):
        if self._reified:
            self._update()
        else:
            self._create()

    def _create(self):
        if self.__class__.SQL_INSERT is None:
            raise NotImplementedError("Can't create model.")

        try:
            db.cursor().execute(self.__class__.SQL_INSERT, self.to_row())
        except Exception:
            db.conn().rollback()
            raise
        else:
            db.conn().commit()
            self._reified = True
            self.id = db.cursor().lastrowid

    def _update(self):
        if self.SQL_UPDATE is None:
            raise NotImplementedError("Can't update model.")

    @classmethod
    def get(cls, _id):
        if cls.SQL_GET is None:
            raise NotImplementedError("Can't get model.")

        db.cursor().execute(cls.SQL_GET, {'id': _id})
        res = db.cursor().fetchone()
        if res is None:
            return None
        else:
            instance = cls.from_row(res)
            instance._reified = True
            return instance

    @classmethod
    def get_all(cls, order_by='id', order='ASC', **kwargs):
        if cls.SQL_GET_ALL is None:
            raise NotImplementedError("Can't get all models.")

        ret = []
        for row in db.cursor().execute(cls.SQL_GET_ALL % (order_by, order)):
            ret.append(cls.from_row(row))

        blacklist = kwargs.get('blacklist')
        if blacklist:
            ret = filter(lambda x: x not in blacklist, ret)

        return ret

    def execute(self, sql, args):
        try:
            db.cursor().execute(sql, args)
        except Exception:
            db.conn().rollback()
            raise
        else:
            db.conn().commit()

    def is_reified(self):
        return self._reified

    def add(self, thing):
        if not self.is_reified():
            raise sqlite3.DatabaseError(
                "Can't add, %s was not reified." % self.__class__)
        elif not thing.is_reified():
            raise sqlite3.DatabaseError(
                "Can't add, %s was not reified." % self.__class__)

    def remove(self, thing):
        if not self.is_reified():
            raise sqlite3.DatabaseError(
                "Can't remove, %s was not reified." % self.__class__)
        elif not thing.is_reified():
            raise sqlite3.DatabaseError(
                "Can't remove, %s was not reified." % self.__class__)


class User(Base):

    SQL_INSERT = '''
        INSERT INTO users (name, email, avatar, status, language, password)
        VALUES (:name, :email, :avatar, :status, :language, :password)
    '''  # noqa

    SQL_GET = '''
        SELECT name, email, avatar, status, language, password
        FROM users WHERE email=:id
    '''

    SQL_GET_ALL = '''
        SELECT name, email, avatar, status, language, password
        FROM users ORDER BY %s %s
    '''

    _config = {
        'hashing_rounds': 800000
    }

    def __init__(self):
        super(User, self).__init__()
        self.name = ''
        self.email = ''
        self.avatar = ''
        self.status = ''
        self.language = ''
        self.password = ''

    @staticmethod
    def from_row(row):
        user = User()
        user.name = row['name']
        user.email = row['email']
        user.avatar = row['avatar']
        user.status = row['status']
        user.language = row['language']
        user.password = row['password']
        return user

    def to_row(self):
        return {
            'name': self.name,
            'email': self.email,
            'avatar': self.avatar,
            'status': self.status,
            'language': self.language,
            'password': self.password,
        }

    def set_password(self, pwd, config=None):
        if config is None:
            config = User._config

        h = hasher.encrypt(pwd, rounds=config['hashing_rounds'])
        self.password = h

    def compare_password(self, pwd):
        return hasher.verify(pwd, self.password)

    def get_id(self):
        return self.email

    def add(self, thing):
        super(User, self).add(thing)
        if type(thing) is Message:
            sql = '''
                INSERT INTO user_messages (owner_id, message_id)
                VALUES (:owner_id, :message_id)
            '''
            args = {
                'owner_id': self.get_id(),
                'message_id': thing.get_id(),
            }
        self.execute(sql, args)

    def get_rooms(self):
        db.cursor().execute('''
            SELECT user_id, room_id
            FROM user_rooms INNER JOIN
            rooms ON user_rooms.room_id=rooms.rid WHERE user_rooms.user_id=:id
        ''', {'id': self.get_id()})  # noqa
        rows = db.cursor().fetchall()
        rooms = []
        for row in rows:
            rooms.append(Room.get(row['room_id']))
        return rooms

    def in_room(self, room):
        rooms = self.get_rooms()
        for r in rooms:
            if room.get_id() == r.get_id():
                return True
        return False

    def get_recent_room(self):
        db.cursor().execute(
            '''
            SELECT room_id FROM user_rooms WHERE user_id=:user_id
            ORDER BY joined_utc DESC
            ''', {'user_id': self.get_id()})
        res = db.cursor().fetchone()
        if res is None:
            return None
        return Room.get(res['room_id'])


class Message(Base):

    def __init__(self):
        super(Message, self).__init__()

        # A client id, used for keeping track of a message generated by client.
        self.client_id = ''

    SQL_INSERT = '''
        INSERT INTO messages (date_utc, content)
        VALUES (:date, :content)
    '''  # noqa

    SQL_GET = '''
        SELECT mid, date_utc as date, content FROM messages WHERE mid=:id
    '''

    SQL_GET_ALL = '''
        SELECT mid, date_utc as date, content FROM messages
        ORDER BY %s %s
    '''

    @staticmethod
    def from_row(row):
        msg = Message()
        msg.id = row['mid']
        msg.date = row['date']
        msg.content = row['content']
        return msg

    def to_row(self):
        try:
            self.date
        except AttributeError:
            self.date = datetime.datetime.now()

        return {
            'mid': self.id,
            'date': self.date,
            'content': self.content,
        }

    def get_id(self):
        return self.id

    def get_owner(self):
        db.cursor().execute('''
            SELECT owner_id, message_id, name, email, avatar, status, language, password
            FROM user_messages INNER JOIN
            users ON user_messages.owner_id=users.email WHERE user_messages.message_id=:id
        ''', {'id': self.get_id()})  # noqa
        row = db.cursor().fetchone()
        if row is None:
            return None
        else:
            return User.from_row(row)

    def add(self, thing):
        super(Message, self).add(thing)
        if type(thing) is Attachment:
            sql = '''
                INSERT INTO messages_attachments (message_id, attachment_id)
                VALUES (:attachment_id, :message_id)
            '''
            args = {
                'attachment_id': thing.get_id(),
                'message_id': self.get_id(),
            }

        self.execute(sql, args)

    def human_readable_date(self):
        today = datetime.datetime.today()
        y = today.year
        m = today.month
        d = today.day
        if (self.date.year == y and self.date.month == m and self.date.day == d):  # noqa
            return self.date.strftime('%H:%M')
        else:
            return self.date.strftime('%a %w. %b, %Y %X')


class Attachment(Base):

    SQL_INSERT = '''
        INSERT INTO attachments (data, size, mime_type)
        VALUES (:data, :size, :mime_type)
    '''  # noqa

    SQL_GET = '''
        SELECT aid, data, size, mime_type FROM attachments WHERE aid=:id
    '''

    SQL_GET_ALL = '''
        SELECT aid, data, size, mime_type FROM attachments
        ORDER BY %s %s
    '''

    @staticmethod
    def from_row(row):
        att = Attachment()
        att.id = row['aid']
        att.data = row['data']
        att.size = row['size']
        att.mime_type = row['mime_type']
        return att

    def to_row(self):
        return {
            'aid': self.id,
            'data': self.data,
            'size': self.size,
            'mime_type': self.mime_type,
        }


class Room(Base):

    SQL_INSERT = '''
        INSERT INTO rooms (
            name, slug, display_name, topic, date_created_utc, deleted, language
        )
        VALUES (:name, :slug, :display_name, :topic, :date_created, :deleted, :language)
    '''  # noqa

    SQL_GET = '''
        SELECT rid, name, slug, display_name, topic, date_created_utc, deleted, language
        FROM rooms WHERE rid=:id
    '''  # noqa

    SQL_GET_ALL = '''
        SELECT rid, name, slug, display_name, topic, date_created_utc, deleted, language FROM rooms
        ORDER BY %s %s
    '''  # noqa

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        return False

    @staticmethod
    def from_row(row):
        room = Room()
        room.id = row['rid']
        room.name = row['name']
        room.slug = row['slug']
        room.display_name = row['display_name']
        room.topic = row['topic']
        room.date_created = row['date_created_utc']
        room.deleted = row['deleted']
        room.language = row['language']
        return room

    def to_row(self):
        try:
            self.date_created
        except AttributeError:
            self.date_created = datetime.datetime.now()

        try:
            self.topic
        except AttributeError:
            self.topic = ''

        try:
            self.display_name
        except AttributeError:
            self.display_name = ''

        try:
            self.deleted
        except AttributeError:
            self.deleted = False

        try:
            self.language
        except AttributeError:
            self.language = 'en'

        return {
            'name': self.name,
            'slug': slugify(self.slug),
            'display_name': self.display_name,
            'topic': self.topic,
            'date_created': self.date_created,
            'deleted': int(self.deleted),
            'language': self.language,
        }

    def get_url(self):
        # TODO: add some sort of baseurl
        return '/room/%s/%s' % (self.get_id(), self.slug)

    def add(self, thing):
        super(Room, self).add(thing)
        if type(thing) is Message:
            sql = '''
                INSERT INTO room_messages (room_id, message_id)
                VALUES (:room_id, :message_id)
            '''
            args = {
                'room_id': self.get_id(),
                'message_id': thing.get_id(),
            }
        elif type(thing) is User:
            sql = '''
                INSERT INTO user_rooms (user_id, room_id, joined_utc)
                VALUES (:user_id, :room_id, :joined)
            '''
            args = {
                'room_id': self.get_id(),
                'user_id': thing.get_id(),
                'joined': datetime.datetime.now()
            }

        self.execute(sql, args)

    def remove(self, thing):
        super(Room, self).remove(thing)
        if type(thing) is User:
            sql = '''
                DELETE FROM user_rooms
                WHERE user_id=:user_id AND room_id=:room_id
            '''
            args = {
                'room_id': self.get_id(),
                'user_id': thing.get_id(),
            }

        self.execute(sql, args)

    def get_messages(self, order_by='date_utc', order='ASC'):
        ret = []
        for row in db.cursor().execute(
            '''
                SELECT mid, content, date_utc as date, room_id, message_id
                FROM room_messages INNER JOIN
                messages ON room_messages.message_id=messages.mid
                WHERE room_messages.room_id=:id ORDER BY %s %s
            ''' % (order_by, order),
                {'id': self.get_id()}):
            ret.append(Message.from_row(row))
        return ret

    def get_messages_from(self, msg_id, order_by='date_utc', order='ASC'):
        ret = []
        for row in db.cursor().execute(
            '''
                SELECT mid, content, date_utc as date, room_id, message_id
                FROM room_messages INNER JOIN
                messages ON room_messages.message_id=messages.mid
                WHERE room_messages.room_id=:id AND mid > :from_mid
                ORDER BY %s %s
            ''' % (order_by, order),
            {
                'id': self.get_id(),
                'from_mid': msg_id,
            }
        ):
            ret.append(Message.from_row(row))
        return ret

    @classmethod
    def get_by_name(cls, name):
        db.cursor().execute(
            '''
            SELECT rid FROM rooms WHERE name=:name
            ''', {'name': name})
        res = db.cursor().fetchone()
        if res is None:
            return None
        return cls.get(res['rid'])

    def contains_user(self, user):
        rooms = user.get_rooms()
        for r in rooms:
            if self.get_id() == r.get_id():
                return True
        return False
