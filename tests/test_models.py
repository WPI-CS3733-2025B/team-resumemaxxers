import warnings

from reportlab.lib.colors import describe

warnings.filterwarnings("ignore")

from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.main.models import *
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class TestModels(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = Student(username='john', firstname='John', lastname='Pork')
        u.set_password('aaa')
        self.assertFalse(u.check_password('bbb'))
        self.assertTrue(u.check_password('aaa'))

    def test_apply(self):
        u = Student(username='john', firstname='John', lastname='Pork', gpa=1.0, email='jp@jpmorgan.com')
        f = Faculty(username='DrBig', firstname='Dr', lastname='Big', id=1)
        self.assertTrue(f.id is not None)
        p = Position(name='Vibe Coder', description='default', team_size=1, min_gpa=4.0, faculty_id=f.id)
        self.assertTrue(len(p.applications)==0)
        u.apply(p)
        self.assertTrue(len(p.applications)==1)
        self.assertTrue(p.applications[0].student == u)
        self.assertTrue(p.applications[0].position == p)
