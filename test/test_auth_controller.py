import os
import src.main
from src.models.user import User
import unittest
import tempfile
import json
import logging

class TestAuthController(unittest.TestCase):

    def setUp(self):
        src.main.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        src.main.app.config['TESTING'] = True
        self.app = src.main.app.test_client()
        with src.main.app.app_context():
            src.main.init_app()

    def tearDown(self):
        pass

    def test_login_success(self):
        login = 'test_user'
        password = 'test_pass'
        src.main.db.session.add(User(login, password))
        src.main.db.session.commit()

        json_payload = {
            "login": login,
            "password": password
        }

        response = self.app.post('/v1/auth/login',
            data = json.dumps(json_payload),
            headers = {'Content-Type': 'application/json'})
        json_response = json.loads(response.data)
        self.assertIsNotNone(json_response['user'])
        self.assertEquals((json_response['user']['login']), login)

    def test_login_incorrect_password(self):
        login = 'test_user'
        password = 'test_pass'
        src.main.db.session.add(User(login, password))
        src.main.db.session.commit()

        json_payload = {
            "login": login,
            "password": "incorrect_pass"
        }

        response = self.app.post('/v1/auth/login',
            data = json.dumps(json_payload),
            headers = {'Content-Type': 'application/json'})
        self.assertEquals(response.status_code, 403)

    def test_logout(self):
        login = 'test_user'
        password = 'test_pass'
        src.main.db.session.add(User(login, password))
        src.main.db.session.commit()

        json_payload = {
            "login": login,
            "password": password
        }

        response = self.app.post('/v1/auth/login',
            data = json.dumps(json_payload),
            headers = {'Content-Type': 'application/json'})
        self.assertEquals(response.status_code, 200)

        token = json.loads(response.get_data())['token']

        logout_json_payload = {
            "token": token
        }

        self.app.post('/v1/auth/logout',
            data = json.dumps(logout_json_payload),
            headers = {'Content-Type': 'application/json'})

        response = self.app.get('/v1/client',
            headers = {'Content-Type': 'application/json', 'token': token})
        self.assertEquals(response.status_code, 403)


    def test_login_inexistent_login(self):
        login = 'test_user'
        password = 'test_pass'
        src.main.db.session.add(User(login, password))
        src.main.db.session.commit()

        json_payload = {
            "login": "inexistent_login",
            "password": password
        }

        response = self.app.post('/v1/auth/login',
            data = json.dumps(json_payload),
            headers = {'Content-Type': 'application/json'})
        self.assertEquals(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()
