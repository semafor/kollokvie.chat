import kollokvie_chat.model as model
import unittest


class TestUsers(unittest.TestCase):

    def test_create_user_from_row(self):
        row = {
            'name': 'Test Person',
            'email': 'test@example.org',
            'avatar': 'avatar',
            'status': 'status',
            'language': 'language',
            'password': 'password',
        }
        user = model.User.from_row(row)

        self.assertEqual(user.name, row['name'])
        self.assertEqual(user.email, row['email'])
        self.assertEqual(user.avatar, row['avatar'])
        self.assertEqual(user.status, row['status'])
        self.assertEqual(user.language, row['language'])
        self.assertEqual(user.password, row['password'])

    def test_create_password(self):
        user = model.User()
        user.set_password('hunter2', {'hashing_rounds': 2000})
        self.assertIsNotNone(user.password)

    def test_compare_password(self):
        user = model.User()
        user.set_password('hunter2', {'hashing_rounds': 2000})
        self.assertTrue(user.compare_password('hunter2'))
        self.assertFalse(user.compare_password('wrong'))


class TestMessages(unittest.TestCase):

    pass


if __name__ == '__main__':
    unittest.main()
