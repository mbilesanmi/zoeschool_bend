import os
import json

from flask_testing import TestCase

from zoeschool_bend.main import create_flask_app
from zoeschool_bend.api.models.models import db


class BaseTestCase(TestCase):

    def create_app(self):
        self.app = create_flask_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        return self.app

    def setUp(self):
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
