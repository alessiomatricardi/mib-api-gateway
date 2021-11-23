import unittest


class RaoTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from mib import create_app
        cls.app = create_app()
