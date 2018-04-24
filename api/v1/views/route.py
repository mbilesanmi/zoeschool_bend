from flask import request, jsonify, json, Response, g
from flask_restful import Resource

from ...authentication.token import token_required


class RouteResource(Resource):
    
    def get(self):
        return {
            'status': 'success',
            'data': { 'message': "successfully created the route resource" }
        }, 200
