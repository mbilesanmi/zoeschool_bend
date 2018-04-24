import os
import logging

from flask_script import Manager, Server, prompt_bool, Shell
from flask_migrate import MigrateCommand
from logging.handlers import RotatingFileHandler
from sqlalchemy.exc import SQLAlchemyError

from main import create_flask_app

try:
    from api.models.models import db
except ImportError:
    from zoeschool_bend.api.models.models import db


environment = os.getenv("FLASK_CONFIG")
app = create_flask_app(environment)

app.secret_key = os.getenv("APP_SECRET")

port = int(os.environ.get('PORT', 5000))
server = Server(host="0.0.0.0", port=port)

def _make_context():
    pass

# initialize flask script
manager = Manager(app)

# enable migration commands
manager.add_command("runserver", server)
manager.add_command("db", MigrateCommand)
manager.add_command("shell", Shell(make_context=_make_context))

@manager.command
def seed_default_data(prompt=True):
    if environment == "production":
        print("\n\n\tNot happening! Aborting...\n\n Aborted\n\n")
        return

    if environment in ["testing", "development"]:
        if (prompt_bool("\n\nAre you sure you want to seed your database, all previous data will be wiped off?")):
            try:
                # drops all the tables 
                db.drop_all()
                db.session.commit()

                # creates all the tables
                db.create_all()
            except SQLAlchemyError as error:
                db.session.rollback()
                print("\n\n\tCommand could not execute due to the error below! Aborting...\n\n Aborted\n\n" + str(error) + "\n\n")
                return

            try:
                pass
            except SQLAlchemyError as error:
                pass
                db.session.rollback()
                message = "\n\n\tThe error below occured when trying to seed the database\n\n\n" + str(error) + "\n\n"

            print(message)

        else:
            print("\n\n\tAborting...\n\n\tAborted\n\n")

    else:
        print("\n\n\tAborting... Invalid environment '{}'.\n\n"
              .format(environment))

# initialize the log handler
handler = RotatingFileHandler('errors.log', maxBytes=10000000, backupCount=5)
formatter = logging.Formatter( "%(asctime)s | %(pathname)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s ")
# set the log handler level
handler.setLevel(logging.INFO)
# set the app logger level
app.logger.setLevel(logging.INFO)
werkzeug_handler = logging.getLogger('werkzeug')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.addHandler(werkzeug_handler)

manager.run()
