import sqlite3
import kollokvie_chat.model as model


CREATE_USERS = '''
CREATE TABLE IF NOT EXISTS users
(
    email text PRIMARY KEY,
    name text,
    avatar text,
    status text,
    language text,
    password text NOT NULL
)
'''

SELECT_SINGLE_USER = '''
SELECT name, email, avatar, status, language, password
FROM users WHERE email=:id
'''

INSERT_USER = '''
INSERT OR REPLACE INTO users (name, email, avatar, status, language, password)
VALUES (:name, :email, :avatar, :status, :language, :password)
'''  # noqa

CREATE_MESSAGES = '''
CREATE TABLE IF NOT EXISTS messages
(
    mid INTEGER PRIMARY KEY,
    date_utc text,
    content text
)
'''

INSERT_MESSAGE = '''
INSERT INTO messages (date_utc, content)
VALUES (:date, :content)
'''

CREATE_USER_MESSAGES = '''
CREATE TABLE IF NOT EXISTS user_messages
(
    umid INTEGER PRIMARY KEY,
    owner_id TEXT,
    message_id TEXT,
    FOREIGN KEY(owner_id) REFERENCES user(email),
    FOREIGN KEY(message_id) REFERENCES messages(mid)
)
'''

LINK_USER_MESSAGE = '''
INSERT INTO user_messages (owner_id, message_id)
VALUES (:owner_id, :message_id)
'''

CREATE_ROOMS = '''
CREATE TABLE IF NOT EXISTS rooms
(
    rid INTEGER PRIMARY KEY,
    name text NOT NULL,
    topic text,
    date_created_utc text,
    deleted number,
    language text
)
'''

CREATE_ROOM = '''
INSERT OR REPLACE INTO rooms (name, topic, date_created_utc, deleted, language)
VALUES (:name, :topic, :date_created, :deleted, :language)
'''

CREATE_ROOM_MESSAGES = '''
CREATE TABLE IF NOT EXISTS room_messages
(
    rmid INTEGER PRIMARY KEY,
    room_id TEXT,
    message_id TEXT,
    FOREIGN KEY(room_id) REFERENCES room(rid),
    FOREIGN KEY(message_id) REFERENCES messages(mid)
)
'''

LINK_ROOM_MESSAGE = '''
INSERT INTO room_messages (room_id, message_id)
VALUES (:room_id, :message_id)
'''

CREATE_ATTACHMENTS = '''
CREATE TABLE IF NOT EXISTS attachments
(
    aid INTEGER PRIMARY KEY,
    data blob,
    size number,
    mime_type text
)
'''


class Database:

    def __init__(self, path):
        self._conn = None
        self._cursor = None
        self._path = path

    def initialize(self):
        self._conn = sqlite3.connect(self._path)
        self._conn.row_factory = sqlite3.Row
        self._cursor = self._conn.cursor()
        try:
            self._cursor.execute('PRAGMA foreign_keys')
            self._cursor.execute(CREATE_MESSAGES)
            self._cursor.execute(CREATE_USERS)
            self._cursor.execute(CREATE_USER_MESSAGES)
            self._cursor.execute(CREATE_ROOMS)
            self._cursor.execute(CREATE_ROOM_MESSAGES)
            self._cursor.execute(CREATE_ATTACHMENTS)
        except Exception:
            self._conn.rollback()
            raise
        else:
            self._conn.commit()

    def cleanup(self):
        if self._cursor is not None:
            self._cursor.close()
        if self._conn is not None:
            self._conn.close()

    def add_user(self, user):
        try:
            self._cursor.execute(INSERT_USER, user.to_row())
        except Exception:
            self._conn.rollback()
            raise
        else:
            self._conn.commit()

    def get_user(self, uid):
        self._cursor.execute(SELECT_SINGLE_USER, {'id': uid})
        res = self._cursor.fetchone()
        if res is None:
            return None
        else:
            return model.User.from_row(res)

    def add_message(self, message):
        try:
            self._cursor.execute(INSERT_MESSAGE, message.to_row())

            if self._cursor.lastrowid < 0:
                raise Exception("Failed to insert message.")
            message.mid = self._cursor.lastrowid
        except Exception:
            self._conn.rollback()
            raise
        else:
            self._conn.commit()

    def link_user_message(self, user, message):
        if message.get_id() < 0:
            raise sqlite3.DatabaseError("Message was not reified.")
        try:
            self._cursor.execute(LINK_USER_MESSAGE, {
                'owner_id': user.get_id(),
                'message_id': message.get_id(),
            })
        except Exception:
            self._conn.rollback()
            raise
        else:
            self._conn.commit()

    def add_room(self, room):
        try:
            self._cursor.execute(CREATE_ROOM, room.to_row())
            if self._cursor.lastrowid < 0:
                raise Exception("Failed to insert room.")
            room.rid = self._cursor.lastrowid
        except Exception:
            self._conn.rollback()
            raise
        else:
            self._conn.commit()

    def link_room_message(self, room, message):
        if room.get_id() < 0:
            raise sqlite3.DatabaseError("Room was not reified.")
        if message.get_id() < 0:
            raise sqlite3.DatabaseError("Message was not reified.")
        try:
            self._cursor.execute(LINK_ROOM_MESSAGE, {
                'room_id': room.get_id(),
                'message_id': message.get_id(),
            })
        except Exception:
            self._conn.rollback()
            raise
        else:
            self._conn.commit()

    def executeSelect(self, sql, args=None):
        '''Perform arbitrary select sql. Return row(s).'''
        if args is not None:
            self._cursor.execute(sql, args)
        else:
            self._cursor.execute(sql)
        return self._cursor.fetchall()
