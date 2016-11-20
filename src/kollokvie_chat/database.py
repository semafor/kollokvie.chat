import sqlite3

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

CREATE_USER_ROOMS = '''
CREATE TABLE IF NOT EXISTS user_rooms
(
    user_id TEXT,
    room_id TEXT,
    joined_utc timestamp,
    FOREIGN KEY(user_id) REFERENCES user(email),
    FOREIGN KEY(room_id) REFERENCES room(rid)
)
'''

CREATE_MESSAGES = '''
CREATE TABLE IF NOT EXISTS messages
(
    mid INTEGER PRIMARY KEY,
    date_utc timestamp,
    content text
)
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

CREATE_ROOMS = '''
CREATE TABLE IF NOT EXISTS rooms
(
    rid INTEGER PRIMARY KEY,
    name text UNIQUE NOT NULL,
    slug text UNIQUE NOT NULL,
    display_name text,
    topic text,
    date_created_utc text,
    deleted number,
    language text
)
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

CREATE_ATTACHMENTS = '''
CREATE TABLE IF NOT EXISTS attachments
(
    aid INTEGER PRIMARY KEY,
    data blob,
    size number,
    mime_type text
)
'''

CREATE_MESSAGES_ATTACHMENTS = '''
CREATE TABLE IF NOT EXISTS messages_attachments
(
    maid INTEGER PRIMARY KEY,
    message_id TEXT,
    attachment_id TEXT,
    FOREIGN KEY(message_id) REFERENCES messages(mid),
    FOREIGN KEY(attachment_id) REFERENCES attachments(aid)
)
'''


class Database(object):

    def __init__(self, path):
        self._conn = None
        self._cursor = None
        self._path = path

    def initialize(self):
        self._conn = sqlite3.connect(self._path,
                                     detect_types=sqlite3.PARSE_DECLTYPES)
        self._conn.row_factory = sqlite3.Row
        self._conn.text_factory = str
        self._cursor = self._conn.cursor()
        try:
            self._cursor.execute('PRAGMA foreign_keys')
            self._cursor.execute(CREATE_MESSAGES)
            self._cursor.execute(CREATE_USERS)
            self._cursor.execute(CREATE_USER_MESSAGES)
            self._cursor.execute(CREATE_ROOMS)
            self._cursor.execute(CREATE_USER_ROOMS)
            self._cursor.execute(CREATE_ROOM_MESSAGES)
            self._cursor.execute(CREATE_ATTACHMENTS)
            self._cursor.execute(CREATE_MESSAGES_ATTACHMENTS)
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

    def cursor(self):
        return self._cursor

    def conn(self):
        return self._conn

    def executeSelect(self, sql, args=None):
        '''Perform arbitrary select sql. Return row(s).'''
        if args is not None:
            self._cursor.execute(sql, args)
        else:
            self._cursor.execute(sql)
        return self._cursor.fetchall()
