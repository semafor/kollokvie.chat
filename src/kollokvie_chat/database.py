import sqlite3
import kollokvie_chat.models as models


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

# SELECT_SINGLE_USER = '''
# SELECT name, email, avatar, status, language, password
# FROM users WHERE email=:id
# '''

# INSERT_USER = '''
# INSERT OR REPLACE INTO users (name, email, avatar, status, language, password)
# VALUES (:name, :email, :avatar, :status, :language, :password)
# '''  # noqa

CREATE_USER_ROOMS = '''
CREATE TABLE IF NOT EXISTS user_rooms
(
    user_id TEXT,
    room_id TEXT,
    FOREIGN KEY(user_id) REFERENCES user(email),
    FOREIGN KEY(room_id) REFERENCES room(rid)
)
'''

# LINK_USER_ROOM = '''
# INSERT INTO user_rooms (user_id, room_id)
# VALUES (:user_id, :room_id)
# '''

# UNLINK_USER_ROOM = '''
# DELETE FROM user_rooms WHERE user_id=:user_id AND room_id=:room_id
# '''

# SELECT_ROOM_MESSAGES = '''
# SELECT mid, content, date_utc as date, room_id, message_id
# FROM room_messages INNER JOIN
# messages ON room_messages.message_id=messages.mid
# WHERE room_messages.room_id=:id
# '''

CREATE_MESSAGES = '''
CREATE TABLE IF NOT EXISTS messages
(
    mid INTEGER PRIMARY KEY,
    date_utc text,
    content text
)
'''

# INSERT_MESSAGE = '''
# INSERT INTO messages (date_utc, content)
# VALUES (:date, :content)
# '''

# SELECT_SINGLE_MESSAGE = '''
# SELECT mid, date_utc as date, content FROM messages WHERE mid=:id
# '''

# SELECT_MESSAGE_OWNER = '''
# SELECT owner_id, message_id, name, email, avatar, status, language, password
# FROM user_messages INNER JOIN
# users ON user_messages.owner_id=users.email WHERE user_messages.message_id=:id
# '''

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

# LINK_USER_MESSAGE = '''
# INSERT INTO user_messages (owner_id, message_id)
# VALUES (:owner_id, :message_id)
# '''

CREATE_ROOMS = '''
CREATE TABLE IF NOT EXISTS rooms
(
    rid INTEGER PRIMARY KEY,
    name text NOT NULL,
    slug text UNIQUE NOT NULL,
    topic text,
    date_created_utc text,
    deleted number,
    language text
)
'''

# CREATE_ROOM = '''
# INSERT INTO rooms (
#     name, slug, topic, date_created_utc, deleted, language
# )
# VALUES (:name, :topic, :slug, :date_created, :deleted, :language)
# '''

# SELECT_ALL_ROOMS = '''
# SELECT rid, name, slug, topic, date_created_utc, deleted, language FROM rooms
# '''

# SELECT_SINGLE_ROOM = '''
# SELECT rid, name, slug, topic, date_created_utc, deleted, language FROM rooms
# WHERE rid=:id
# '''

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

# LINK_ROOM_MESSAGE = '''
# INSERT INTO room_messages (room_id, message_id)
# VALUES (:room_id, :message_id)
# '''

CREATE_ATTACHMENTS = '''
CREATE TABLE IF NOT EXISTS attachments
(
    aid INTEGER PRIMARY KEY,
    data blob,
    size number,
    mime_type text
)
'''

# CREATE_ATTACHMENT = '''
# INSERT INTO attachments (data, size, mime_type)
# VALUES (:data, :size, :mime_type)
#'''

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

# LINK_MESSAGE_ATTACHMENT = '''
# INSERT INTO messages_attachments (message_id, attachment_id)
# VALUES (:attachment_id, :message_id)
# '''


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

    # def add_user(self, user):
    #     try:
    #         self._cursor.execute(INSERT_USER, user.to_row())
    #     except Exception:
    #         self._conn.rollback()
    #         raise
    #     else:
    #         self._conn.commit()

    # def get_user(self, uid):
    #     self._cursor.execute(SELECT_SINGLE_USER, {'id': uid})
    #     res = self._cursor.fetchone()
    #     if res is None:
    #         return None
    #     else:
    #         return models.User.from_row(res)

    # def get_single(self, model, dbid):
    #     sql = None
    #     if model == models.Room:
    #         sql = SELECT_SINGLE_ROOM
    #     elif model == models.Message:
    #         sql = SELECT_SINGLE_MESSAGE

    #     if sql is None:
    #         raise NotImplementedError(
    #             "Not implemented for model %s." % str(model)
    #         )

    #     self._cursor.execute(sql, {'id': dbid})
    #     res = self._cursor.fetchone()
    #     if res is None:
    #         return None
    #     else:
    #         return model.from_row(res)

    # def add_message(self, message):
    #     try:
    #         self._cursor.execute(INSERT_MESSAGE, message.to_row())

    #         if self._cursor.lastrowid < 0:
    #             raise Exception("Failed to insert message.")
    #         message.id = self._cursor.lastrowid
    #     except Exception:
    #         self._conn.rollback()
    #         raise
    #     else:
    #         self._conn.commit()

    # def link_user_message(self, user, message):
    #     if not type(user) is models.User:
    #         raise TypeError('First argument not a User.')

    #     if not type(message) is models.Message:
    #         raise TypeError('First argument not a Message.')

    #     if message.get_id() < 0:
    #         raise sqlite3.DatabaseError("Message was not reified.")
    #     try:
    #         self._cursor.execute(LINK_USER_MESSAGE, {
    #             'owner_id': user.get_id(),
    #             'message_id': message.get_id(),
    #         })
    #     except Exception:
    #         self._conn.rollback()
    #         raise
    #     else:
    #         self._conn.commit()

    # def link_user_room(self, user, room):
    #     if not type(user) is models.User:
    #         raise TypeError('First argument not a User.')

    #     if not type(room) is models.Room:
    #         raise TypeError('First argument not a Room.')

    #     if room.get_id() < 0:
    #         raise sqlite3.DatabaseError("Room was not reified.")

    #     if self.get_user_in_room(user, room):
    #         print('User %s already in room %s' % (user.get_id(), room.name))
    #         return

    #     try:
    #         self._cursor.execute(LINK_USER_ROOM, {
    #             'user_id': user.get_id(),
    #             'room_id': room.get_id(),
    #         })
    #     except Exception:
    #         self._conn.rollback()
    #         raise
    #     else:
    #         self._conn.commit()

    # def unlink_user_room(self, user, room):
    #     if not type(user) is models.User:
    #         raise TypeError('First argument not a User.')

    #     if not type(room) is models.Room:
    #         raise TypeError('First argument not a Room.')

    #     if room.get_id() < 0:
    #         raise sqlite3.DatabaseError("Room was not reified.")
    #     try:
    #         self._cursor.execute(UNLINK_USER_ROOM, {
    #             'user_id': user.get_id(),
    #             'room_id': room.get_id(),
    #         })
    #     except Exception:
    #         self._conn.rollback()
    #         raise
    #     else:
    #         self._conn.commit()

    # def get_user_in_room(self, user, room):
    #     self._cursor.execute('''
    #         SELECT * FROM user_rooms WHERE user_id=:user_id AND
    #         room_id=:room_id
    #     ''', {'user_id': user.get_id(), 'room_id': room.get_id()})
    #     return self._cursor.fetchone() is not None

    # def add_room(self, room):
    #     try:
    #         self._cursor.execute(CREATE_ROOM, room.to_row())
    #         if self._cursor.lastrowid < 0:
    #             raise Exception("Failed to insert room.")
    #         room.id = self._cursor.lastrowid
    #     except Exception:
    #         self._conn.rollback()
    #         raise
    #     else:
    #         self._conn.commit()

    # def link_room_message(self, room, message):
    #     if not type(message) is models.Message:
    #         raise TypeError('First argument not a Message.')

    #     if not type(room) is models.Room:
    #         raise TypeError('First argument not a Room.')

    #     if room.get_id() < 0:
    #         raise sqlite3.DatabaseError("Room was not reified.")
    #     if message.get_id() < 0:
    #         raise sqlite3.DatabaseError("Message was not reified.")
    #     try:
    #         self._cursor.execute(LINK_ROOM_MESSAGE, {
    #             'room_id': room.get_id(),
    #             'message_id': message.get_id(),
    #         })
    #     except Exception:
    #         self._conn.rollback()
    #         raise
    #     else:
    #         self._conn.commit()

    # def get_messages(self, room):
    #     ret = []
    #     for row in self._cursor.execute(SELECT_ROOM_MESSAGES,
    #                                     {'id': room.get_id()}):
    #         print(row.keys())
    #         ret.append(models.Message.from_row(row))
    #     return ret

    # def get_message_owner(self, message):
    #     self._cursor.execute(SELECT_MESSAGE_OWNER,
    #                          {'id': message.get_id()})
    #     row = self._cursor.fetchone()
    #     if row is None:
    #         return None
    #     else:
    #         return models.User.from_row(row)

    # def add_attachment(self, attachment):
    #     try:
    #         self._cursor.execute(CREATE_ATTACHMENT, attachment.to_row())
    #         if self._cursor.lastrowid < 0:
    #             raise Exception("Failed to insert attachment.")
    #         attachment.id = self._cursor.lastrowid
    #     except Exception:
    #         self._conn.rollback()
    #         raise
    #     else:
    #         self._conn.commit()

    # def link_attachment_message(self, message, attachment):
    #     if not type(message) is models.Message:
    #         raise TypeError('First argument not a Message.')

    #     if not type(attachment) is models.Attachment:
    #         raise TypeError('First argument not a Attachment.')

    #     if attachment.get_id() < 0:
    #         raise sqlite3.DatabaseError("Attachment was not reified.")
    #     if message.get_id() < 0:
    #         raise sqlite3.DatabaseError("Message was not reified.")
    #     try:
    #         self._cursor.execute(LINK_MESSAGE_ATTACHMENT, {
    #             'attachment_id': attachment.get_id(),
    #             'message_id': message.get_id(),
    #         })
    #     except Exception:
    #         self._conn.rollback()
    #         raise
    #     else:
    #         self._conn.commit()

    # def get_all(self, model):
    #     sql = None
    #     if model == models.Room:
    #         sql = SELECT_ALL_ROOMS

    #     if sql is None:
    #         raise NotImplementedError(
    #             "Not implemented for model %s." % str(model)
    #         )

    #     ret = []
    #     for row in self._cursor.execute(sql):
    #         ret.append(model.from_row(row))
    #     return ret

    def executeSelect(self, sql, args=None):
        '''Perform arbitrary select sql. Return row(s).'''
        if args is not None:
            self._cursor.execute(sql, args)
        else:
            self._cursor.execute(sql)
        return self._cursor.fetchall()
