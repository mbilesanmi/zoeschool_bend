import os
from os.path import join, dirname
from dotenv import load_dotenv

from flask import Flask, jsonify
from flask_sslify import SSLify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, abort


try:
    from config import app_configuration
    from api.v1.views.route import RouteResource
except ImportError:
    from zoeschool_bend.config import app_configuration
    from zoeschool_bend.api.v1.views.route import RouteResource


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def create_flask_app(environment):
    app = Flask(__name__, instance_relative_config=True, static_folder=None, template_folder='./api/emails/templates')
    app.config.from_object(app_configuration[environment])
    app.config['BUNDLE_ERRORS'] = True

    try:
        from api.models import models
    except ImportError:
        from zoeschool_bend.api.models import models

    # to allow cross origin resource sharing
    CORS(app)

    # initialize SQLAlchemy
    models.db.init_app(app)

    # initilize migration commands
    Migrate(app, models.db)

    # initilize api resources
    api = Api(app)

    environment = os.getenv("FLASK_CONFIG")

    # to redirect all incoming requests to https
    if environment.lower() == "production":
        sslify = SSLify(app, subdomains=True, permanent=True)

    # Landing page
    @app.route('/')
    def index():
        return "Welcome to the ZoeSchool Api"

    ##
    ## Actually setup the Api resource routing here
    ##
    api.add_resource(RouteResource, '/api/v1/route', '/api/v1/route/', endpoint='single_route')


    # handle default 404 exceptions with a custom response
    @app.errorhandler(404)
    def resource_not_found(exception):
        response = jsonify(dict(status='fail', data={
                    'error':'Not found', 'message':'The requested URL was'
                    ' not found on the server. If you entered the URL '
                    'manually please check and try again'
                }))
        response.status_code = 404
        return response

    # handle default 500 exceptions with a custom response
    @app.errorhandler(500)
    def internal_server_error(error):
        response = jsonify(dict(status=error,error='Internal Server Error',
                    message='The server encountered an internal error and was' 
                    ' unable to complete your request.  Either the server is'
                    ' overloaded or there is an error in the application'))
        response.status_code = 500
        return response

    return app

# enable flask commands
app = create_flask_app(os.getenv("FLASK_CONFIG"))
