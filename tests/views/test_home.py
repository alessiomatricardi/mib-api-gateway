from .view_test import ViewTest
from faker import Faker


class TestHome(ViewTest):
    faker = Faker()

    BASE_URl = 'http://localhost'

    @classmethod
    def setUpClass(cls):
        super(TestHome, cls).setUpClass()

    def test_home(self):
        rv = self.client.get(self.BASE_URL+'/')
        print(rv)
        assert rv.status_code == 200