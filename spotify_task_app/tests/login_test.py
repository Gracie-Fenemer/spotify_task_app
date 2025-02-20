import unittest
from app import app, db
from models import User
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import url_for

engine = create_engine('mysql+pymysql://USERNAME:PASSWORD@localhost/ManagerTest') #enter valid username and password for testing db

# Create a session factory
Session = sessionmaker(bind=engine)
session = scoped_session(Session)

class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create and configure the app for testing
        cls.app = app 
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://USERNAME:PASSWORD@localhost/ManagerTest'
        cls.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        cls.app.config['SECRET_KEY'] = 'your_secret_key'
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.app.config['SERVER_NAME'] = 'localhost:5003'

        cls.client = cls.app.test_client()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()  # Push a new app context for each test

        db.create_all()  # Create database schema

    def tearDown(self):
        db.session.remove()  # Remove any active sessions
        meta = db.metadata  # contains DB data
        for table in reversed(
                meta.sorted_tables):  # iterates in reverse if fk_contraints in DB - deletes child tables first
            db.session.execute(table.delete())  # executes sql delete command
        db.session.commit()  # commits transaction to DB
        self.app_context.pop()  # Pop the app context

    def test_login_page(self):
        #Test that the login page appears correctly
        response = self.client.get(url_for('login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to The Manager', response.data)
        self.assertIn(b'Please enter your login details:', response.data)
        self.assertIn(b'If you don\'t have an account, you can create one', response.data)

    def test_login_success(self):
        #Test that a user is able to login with correct credentials
        with self.app.app_context():
            user = User(username='testuser2', name='Test User2')
            user.set_password('testpassword2')
            db.session.add(user)
            db.session.commit()

        response = self.client.post(url_for('login'), data=dict(username='testuser2', password='testpassword2'))
        self.assertEqual(response.status_code, 302)  # Page should be redirected -302
        self.assertEqual(response.location, '/app')

    def test_signup_success(self):
        #Test for sign up success
        response = self.client.post('/signup', data=dict(username='newuser4', name='New User', password='newpassword4'))
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertEqual(response.location, '/app')

        with self.app.app_context():
            user = User.query.filter_by(username='newuser4').first()
            self.assertIsNotNone(user)
            self.assertTrue(user.check_password('newpassword4'))

    def test_signup_failure(self):
        #Test for sign up with existing username - fail
        with self.app.app_context():
            user = User(username='existinguser5', name='Existing User5')
            user.set_password('existingpassword')
            db.session.add(user)
            db.session.commit()

        response = self.client.post('/signup', data=dict(username='existinguser5', name='Another User', password='newpassword5'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Username already exists. Please choose a different one.', response.data)

    def test_login_redirect_when_authenticated(self):
        #Test that authenticated users are redirected to the home page
        with self.app.app_context():
            # Create and add a test user
            user = User(username='testuser6', name='Test User6')
            user.set_password('testpassword6')
            db.session.add(user)
            db.session.commit()

        # Simulate login
        response = self.client.post('/', data=dict(username='testuser6', password='testpassword6'))

        # Check if the response is a redirect
        self.assertEqual(response.status_code, 302)  # 302 indicates a redirect
        print(response.location)
        # Check the redirection URL
        self.assertEqual(response.location, '/app')


    def test_logout(self):
        #Test that users can log out
        with self.app.app_context():
            user = User(username='testuser1', name='Test User1')
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()

        self.client.post('/login', data=dict(username='testuser1', password='testpassword1'))
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/')

        #session is terminated
        with self.client.session_transaction() as session:
            self.assertNotIn('username', session)

if __name__ == '__main__':
    unittest.main()

