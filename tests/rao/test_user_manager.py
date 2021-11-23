from unittest.mock import Mock, patch
from flask import current_app
from faker import Faker
from random import randint, choice
from werkzeug.exceptions import HTTPException
import requests

from mib.auth.user import User
from .rao_test import RaoTest


class TestUserManager(RaoTest):

    faker = Faker('it_IT')

    def setUp(self):
        super(TestUserManager, self).setUp()
        from mib.rao.user_manager import UserManager
        self.user_manager = UserManager
        from mib import app
        self.app = app

    def generate_user(self, type):
        extra_data = {
            'firstname': "Mario",
            'lastname': "Rossi",
            'birthdate': TestUserManager.faker.date(),
            'phone': TestUserManager.faker.phone_number()
        }

        data = {
            'id': randint(0, 999),
            'email': TestUserManager.faker.email(),
            'is_active' : choice([True,False]),
            'authenticated': choice([True,False]),
            'is_anonymous': False,
            'type': type,
            'extra': extra_data,
        }

        user = User(**data)
        return user

    @patch('mib.rao.user_manager.requests.get')
    def test_get_user_by_id(self, mock_get):
        user = self.generate_user(type='operator')
        mock_get.return_value = Mock(
            status_code=200,
            json = lambda:{
                'id':user.id,
                'email':user.email,
                'is_active': False,
                'authenticated': False,
                'is_anonymous': False,
                'type': user.type
            }
        )
        response = self.user_manager.get_user_by_id(id)
        assert response is not None

    @patch('mib.rao.user_manager.requests.get')
    def test_get_user_by_id_error(self, mock):
        mock.side_effect = requests.exceptions.Timeout()
        mock.return_value = Mock(status_code=400, json=lambda : {'message': 0})
        with self.assertRaises(HTTPException) as http_error:
            self.user_manager.get_user_by_id(randint(0, 999))
            self.assertEqual(http_error.exception.code, 500)

    @patch('mib.rao.user_manager.requests.get')
    def test_get_user_by_email(self, mock_get):
        user = self.generate_user(type='customer')
        mock_get.return_value = Mock(
            status_code=200,
            json = lambda:{
                'id':user.id,
                'email':user.email,
                'is_active': False,
                'authenticated': False,
                'is_anonymous': False,
                'type': user.type
            }
        )
        response = self.user_manager.get_user_by_email(user.email)
        assert response is not None
    
    @patch('mib.rao.user_manager.requests.get')
    def test_get_user_by_email_error(self, mock):
        mock.side_effect = requests.exceptions.Timeout()
        mock.return_value = Mock(status_code=400, json=lambda : {'message': 0})
        email = TestUserManager.faker.email()
        with self.assertRaises(HTTPException) as http_error:
            self.user_manager.get_user_by_email(email)
            self.assertEqual(http_error.exception.code, 500)

    @patch('mib.rao.user_manager.requests.get')
    def test_get_user_by_phone(self, mock_get):
        user = self.generate_user(type='customer')
        mock_get.return_value = Mock(
            status_code=200,
            json = lambda:{
                'id':user.id,
                'email':user.email,
                'is_active': False,
                'authenticated': False,
                'is_anonymous': False,
                'type': user.type
            }
        )
        response = self.user_manager.get_user_by_phone(user.phone)
        assert response is not None
    
    @patch('mib.rao.user_manager.requests.get')
    def test_get_user_by_phone_error(self, mock):
        mock.side_effect = requests.exceptions.Timeout()
        mock.return_value = Mock(status_code=400, json=lambda : {'message': 0})
        phone = TestUserManager.faker.phone_number()
        with self.assertRaises(HTTPException) as http_error:
            self.user_manager.get_user_by_phone(phone)
            self.assertEqual(http_error.exception.code, 500)

    @patch('mib.rao.user_manager.requests.delete')
    def test_delete_user(self, mock_get):
        user = self.generate_user(type='operator')
        mock_get.return_value = Mock(status_code=200)        

        with self.app.test_request_context ():
            response = self.user_manager.delete_user(user_id=user.id)            
            assert response is not None

    @patch('mib.rao.user_manager.requests.delete')
    def test_delete_user_error(self, mock):
        mock.side_effect = requests.exceptions.Timeout()
        mock.return_value = Mock(status_code=400, json=lambda : {'message': 0})
        with self.app.test_request_context ():
            with self.assertRaises(HTTPException) as http_error:
                self.user_manager.delete_user(user_id=randint(0,999))
                self.assertEqual(http_error.exception.code, 500)

    @patch('mib.rao.user_manager.requests.post')
    def test_authenticate_user(self, mock_post):        
        user = self.generate_user(type='operator')
        user_data = {
            'id': user.id,
            'email': user.email,
            'is_active': False,
            'authenticated': False,
            'is_anonymous': False,
            'type': user.type
        }
        mock_post.return_value = Mock(
            status_code=200,
            json = lambda:{
                'user': user_data
            }
        )
        password = TestUserManager.faker.password()
        response = self.user_manager.authenticate_user(
            email=user.email, password=password
        )
        assert response is not None

    @patch('mib.rao.user_manager.requests.post')
    def test_authenticate_user_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout()
        mock_post.return_value = Mock(status_code=400, json=lambda : {'message': 0})
        with self.app.test_request_context ():
            with self.assertRaises(HTTPException) as http_error:
                self.user_manager.authenticate_user(
                    self.faker.email(),
                    self.faker.password()
                )
                self.assertEqual(http_error.exception.code, 500)
