# models
import os
import json
import enum

from datetime import datetime
from alembic import op
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref, relationship

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.types import JSON, TEXT, TypeDecorator
from sqlalchemy import event, and_
from werkzeug import generate_password_hash, check_password_hash

try:
    from ..generator.id_generator import PushID
except ImportError:
    from zoeschool_bend.api.generator.id_generator import PushID


# snake to camel casing function
def to_camel_case(snake_str):
    title_str = snake_str.title().replace("_", "")
    return title_str[0].lower() + title_str[1:]


class StringyJSON(TypeDecorator):
    """Stores and retrieves JSON as TEXT."""

    impl = TEXT

    def process_bind_param(self, value, dialect):
        """Map value into json data."""
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        """Map json data to python dictionary."""
        if value is not None:
            value = json.loads(value)
        return value


# TypeEngine.with_variant says "use StringyJSON instead when
# connecting to 'sqlite'"
MagicJSON = JSON().with_variant(StringyJSON, 'sqlite')

type_map = {'sqlite': MagicJSON, 'postgresql': JSON}
json_type = type_map[os.getenv("DB_TYPE")]

db = SQLAlchemy()

class ModelViewsMix(object):

    def serialize(self):
        return {to_camel_case(column.name): getattr(self, column.name)
                for column in self.__table__.columns}

    def save(self):
        """Saves an instance of the model to the database."""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except SQLAlchemyError as error:
            db.session.rollback()
            return error
    
    def delete(self):
        """Delete an instance of the model from the database."""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except SQLAlchemyError as error:
            db.session.rollback()
            return error


# enums
class SampleEnum(enum.Enum):
    pass


# models
class SampleModel(db.Model, ModelViewsMix):
    __tablename__ = 'SampleModel'

    id = db.Column(db.String, primary_key=True)


def fancy_id_generator(mapper, connection, target):
    '''
    A function to generate unique identifiers on insert
    '''
    push_id = PushID()
    target.id = push_id.next_id()

# associate the listener function with models, to execute during the
# "before_insert" event
tables = [
           SampleModel
        ]

for table in tables:
    event.listen(table, 'before_insert', fancy_id_generator)
