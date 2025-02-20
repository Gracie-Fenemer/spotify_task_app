import unittest
from flask import session
from app import app, sp_oauth, cache_handler


class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret'
        self.client = app.test_client()
        self.client.testing = True

    def test_spotify_home_redirects(self):
        """Test that /spotify redirects to the Spotify authorization page if not logged in"""
        with self.client as client:
            response = client.get('/spotify')
            self.assertEqual(response.status_code, 302)  # Expecting a redirect

    def test_home_page_redirects(self):
        """Test that /home-page redirects to the Spotify authorization page if not logged in"""
        with self.client as client:
            response = client.get('/home_page')
            self.assertEqual(response.status_code, 302)  # Expecting a redirect

    def test_album_sza_redirects(self):
        """Test that /home_page/cleaning (and all other endpoints below)
        redirects to the Spotify authorization page if not logged in"""
        with self.client as client:
            response = client.get('/home_page/cleaning')
            self.assertEqual(response.status_code, 302)  # Expecting a redirect

    def test_album_sam_smith_redirects(self):
        with self.client as client:
            response = client.get('/home_page/cooking')
            self.assertEqual(response.status_code, 302)  # Expecting a redirect

    def test_gardening_playlist_redirects(self):
        with self.client as client:
            response = client.get('/home_page/gardening')
            self.assertEqual(response.status_code, 302)  # Expecting a redirect

    def test_diy_playlist_redirects(self):
        with self.client as client:
            response = client.get('/home_page/diy')
            self.assertEqual(response.status_code, 302)  # Expecting a redirect

    def test_childcare_playlist_redirects(self):
        with self.client as client:
            response = client.get('/home_page/childcare')
            self.assertEqual(response.status_code, 302)  # Expecting a redirect

    def test_home_playlist_redirects(self):
        with self.client as client:
            response = client.get('/home_page/home')
            self.assertEqual(response.status_code, 302)  # Expecting a redirect

    def test_laundry_playlist_redirects(self):
        with self.client as client:
            response = client.get('/home_page/laundry')
            self.assertEqual(response.status_code, 302)  # Expecting a redirect

    def test_shopping_playlist_redirects(self):
        with self.client as client:
            response = client.get('/home_page/shopping')
            self.assertEqual(response.status_code, 302)  # Expecting a redirect

    def test_pets_playlist_redirects(self):
        with self.client as client:
            response = client.get('/home_page/pets')
            self.assertEqual(response.status_code, 302)  # Expecting a redirect

    def test_finance_playlist_redirects(self):
        with self.client as client:
            response = client.get('/home_page/finance')
            self.assertEqual(response.status_code, 302)  # Expecting a redirect

    def test_logout_clears_session(self):
        """Test that /home_page/logout clears the session and redirects to the home page"""
        with self.client as client:
            with client.session_transaction() as sess:
                sess['token_info'] = 'some_token'
            response = client.get('/home_page/logout')
            self.assertEqual(response.status_code, 302)  # Expecting a redirect
            self.assertNotIn('token_info', session)


if __name__ == '__main__':
    unittest.main()