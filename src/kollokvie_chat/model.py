from passlib.hash import sha256_crypt as hasher


class Base:

    def __init__(self):
        self.id = -1

    def get_id(self):
        return self.id


class User:

    _config = {
        'hashing_rounds': 800000
    }

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

    def __init__(self):
        pass

    def set_password(self, pwd, config=None):
        if config is None:
            config = User._config

        h = hasher.encrypt(pwd, rounds=config['hashing_rounds'])
        self.password = h

    def compare_password(self, pwd):
        return hasher.verify(pwd, self.password)

    def get_id(self):
        return self.email


class Message(Base):

    @staticmethod
    def from_row(row):
        msg = Message()
        msg.id = row['mid']
        msg.date = row['date']
        msg.content = row['content']
        return msg

    def to_row(self):
        return {
            'mid': self.id,
            'date': self.date,
            'content': self.content,
        }

    def get_id(self):
        return self.id


class Attachment(Base):

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

    @staticmethod
    def from_row(row):
        room = Room()
        room.id = row['rid']
        room.name = row['name']
        room.topic = row['topic']
        room.date_created = row['date_created']
        room.deleted = row['deleted']
        room.language = row['language']
        return room

    def to_row(self):
        return {
            'name': self.name,
            'topic': self.topic,
            'date_created': self.date_created,
            'deleted': int(self.deleted),
            'language': self.language,
        }
