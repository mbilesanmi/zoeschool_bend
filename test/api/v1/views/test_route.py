import json
import pytest
from datetime import date

from zoeschool_bend.test.base import BaseTestCase
from zoeschool_bend.api.models.models import db


class NodeTypeTestCase(BaseTestCase):

    def setUp(self):
        db.drop_all()
        db.create_all()
    
    # Test demo route
    def test_demo_route(self):
        response = self.client.get('api/v1/route', content_type='application/json')
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data']['message'],
            'successfully created the route resource')
        self.assert200(response)
