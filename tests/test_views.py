import kollokvie_chat.database as database
import kollokvie_chat.models as models
import kollokvie_chat.views as views


import unittest
from bottle import HTTPResponse


class FakeLoginPlugin:

    def __init__(self):
        self.logged_in = None
        self.user = None

    def get_user(self):
        return self.user

    def login_user(self, user_id):
        self.logged_in = user_id


class FakeApp:

    def __init__(self):
        self.plugins = []
        self.config = {
            'TMPL_FOLDER': 'src/kollokvie_chat/templates/'
        }

    def _add_plugin(self, plugin):
        self.plugins.append(plugin)


class FakeForm:

    def __init__(self):
        self.vals = None

    def set(self, vals):
        self.vals = vals

    def get(self, what):
        return self.vals[what]


class FakeRequest:

    def __init__(self):
        self.forms = None
        self.app = None


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.db = database.Database(':memory:')
        self.db.initialize()
        views.db = self.db
        models.db = self.db

        self.request = FakeRequest()
        self.login_plugin = FakeLoginPlugin()
        self.forms = FakeForm()
        self.app = FakeApp()
        self.app._add_plugin(self.login_plugin)
        self.request.app = self.app
        self.request.forms = self.forms
        views.request = self.request

    def tearDown(self):
        self.db.cleanup()
        del self.db


class BaseLoggedInCase(BaseTestCase):

    def setUp(self):
        super(BaseLoggedInCase, self).setUp()
        user = models.User()
        user.email = 'test@example.org'
        user.save()
        self.user = user
        self.login_plugin.user = user


class TestSignup(BaseTestCase):

    def test_not_logged_in(self):
        out = views.signup_get()
        self.assertIn('Your name', out)
        self.assertIn('Email', out)
        self.assertIn('Password', out)

    def test_errors(self):
        errors = ['have email']
        out = views.signup_error(errors)
        self.assertIn(errors[0], out)

    def test_success(self):
        vals = {
            'name': 'Jonas',
            'password': 'hunter2',
            'email': 'jonas@example.org',
        }
        self.request.forms.set(vals)

        with self.assertRaises(HTTPResponse):
            views.signup_post()

        res = self.db.executeSelect('SELECT * FROM users')
        self.assertEqual(res[0]['name'], vals['name'])
        self.assertEqual(res[0]['email'], vals['email'])

        # return redirect('/login')

    def test_duplicate_email(self):
        user = models.User()
        user.email = 'jonas@example.org'
        user.save()

        vals = {
            'name': 'Jonas',
            'password': 'hunter2',
            'email': 'jonas@example.org',
        }
        self.request.forms.set(vals)

        out = views.signup_post()
        self.assertIn('already exist', out)

    def test_no_password(self):
        vals = {
            'name': 'Jonas',
            'password': '',
            'email': 'jonas@example.org',
        }
        self.request.forms.set(vals)

        out = views.signup_post()
        self.assertIn('enter a password', out)


class TestRoom(BaseLoggedInCase):

    def test_view_rooms(self):
        room = models.Room()
        room.name = 'room name'
        room.slug = 'foo-bar'
        room.topic = 'topic'
        room.save()

        message = models.Message()
        message.content = 'some message'
        message.save()
        self.user.add(message)
        room.add(message)

        out = views.room(room.get_id(), room.slug)
        self.assertIn(room.name, out)
        self.assertIn(message.content, out)

    def test_view_part(self):
        room = models.Room()
        room.name = 'room name'
        room.slug = 'foo-bar'
        room.save()
        room.add(self.user)

        with self.assertRaises(HTTPResponse):
            views.room_part(room.get_id(), room.slug)

    def test_view_say(self):
        room = models.Room()
        room.name = 'room name'
        room.slug = 'foo-bar'
        room.save()
        room.add(self.user)

        vals = {'message': 'some-message', 'client_id': 'foo'}
        self.forms.set(vals)

        views.room_say(room.get_id(), room.slug)

        self.assertEqual(len(room.get_messages()), 1)
        self.assertEqual(room.get_messages()[0].content, 'some-message')
        self.assertEqual(room.get_messages()[0].get_owner().get_id(),
                         self.user.get_id())

    def test_messages_from(self):
        room = models.Room()
        room.name = 'room name'
        room.slug = 'foo-bar'
        room.save()

        message1 = models.Message()
        message1.content = 'first'
        message1.save()
        self.user.add(message1)
        room.add(message1)

        message2 = models.Message()
        message2.content = 'second'
        message2.save()
        self.user.add(message2)
        room.add(message2)

        out = views.messages_from(room.get_id(), room.slug, 1)
        self.assertIn(message2.content, out)
        self.assertNotIn(message1.content, out)
