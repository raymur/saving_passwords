import unittest
from endpoints import app, db
from sqlalchemy.orm import sessionmaker, scoped_session

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = app.test_client()
        self.client.testing = True
        self.context = self.app.app_context()
        self.context.push()
        self.connection = db.engine.connect()
        self.transaction = self.connection.begin()
        SessionFactory = sessionmaker(bind=self.connection)
        self.session = scoped_session(SessionFactory)
        db.session = self.session

    def tearDown(self):
        """Rollback the transaction and close the session."""
        self.session.remove()
        self.transaction.rollback()  # Roll back the transaction
        self.connection.close()
        self.context.pop()

    def test_valid_post_request(self):
        response = self.client.post(
            '/create_user',
            json={'username': '2', 'password': 'password'}  # Sending JSON data
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('added user', response.get_json())
        response = self.client.post(
            '/validate_user',
            json={'username': '2', 'password': 'password'}  # Sending JSON data
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Valid password', response.get_json().get('success'))

    def test_valid_post_request(self):
        response = self.client.post(
            '/create_user',
            json={'username': '3', 'password': 'password'}  # Sending JSON data
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('added user', response.get_json())
        response = self.client.post(
            '/validate_user',
            json={'username': '3', 'password': 'not_a_hotdog'}  # Sending JSON data
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid password', response.get_json().get('error'))


if __name__ == '__main__':
    unittest.main()
