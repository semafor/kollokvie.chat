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
        self.db.add_user(user)

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
