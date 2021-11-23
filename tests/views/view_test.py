import unittest
from faker import Faker
from random import choice, randint


class ViewTest(unittest.TestCase):
    faker = Faker()

    BASE_URL = "http://localhost"

    @classmethod
    def setUpClass(cls):
        from mib import create_app
        cls.app = create_app()
        cls.client = cls.app.test_client()
        from mib.rao.user_manager import UserManager
        cls.user_manager = UserManager

    def login_test_user(self):
        """
        Simulate the customer login for testing the views with @login_required
        :return: customer
        """
        user = self.generate_user()
        response = self.user_manager.create_user(
                'customer',
                user.get('email'),
                user.get('password'),
                user.get('firstname'),
                user.get('lastname'),
                user.get('birthdate'),
                user.get('phone')
                )

        rv = self.client.post(
            self.BASE_URL+'/login',
            json=user
        )
        return user
    
    def generate_user(self):
        """Generates a random user, depending on the type
        Returns:
            (dict): a dictionary with the user's data
        """

        data = {
            'id': randint(0,999),
            'email': self.faker.email(),
            'password': self.faker.password(),
            'is_active' : choice([True,False]),
            'authenticated': False,
            'is_anonymous': False,
            'firstname': self.faker.first_name(),
            'lastname': self.faker.last_name(),
            'birthdate': self.faker.date(),
            'phone': self.faker.phone_number()
        }
        return data
