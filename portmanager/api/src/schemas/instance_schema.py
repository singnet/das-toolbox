from marshmallow import Schema, fields, validate


class InstanceCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    metadata = fields.Dict(required=False)


class InstanceUpdateSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=1))
    metadata = fields.Dict(required=False)


class InstanceResponseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    metadata = fields.Dict()
