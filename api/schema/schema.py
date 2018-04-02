from marshmallow import Schema, fields, validate, pre_load, post_dump, validates_schema, ValidationError
from datetime import datetime as dt


def check_unknown_fields(data, original_data, fields):
    unknown = set(original_data) - set(fields)
    if unknown:
        raise ValidationError('{} is not a valid field'.format(), unknown)


class SampleSchema(Schema):
    pass

    @validates_schema(pass_original=True)
    def unknown_fields(self, data, original_data):
        check_unknown_fields(data, original_data, self.fields)


sample_schema = SampleSchema()
