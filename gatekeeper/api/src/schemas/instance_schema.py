from marshmallow import Schema, fields, validate


class InstanceCreateSchema(Schema):
    instance_id = fields.String(required=True, validate=validate.Length(1, 255))
    name = fields.String(required=True, validate=validate.Length(min=1))
    metadata = fields.Dict(required=False)


class InstanceUpdateSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=1))
    metadata = fields.Dict(required=False)


class InstanceResponseSchema(Schema):
    id = fields.Str(required=True) 
    name = fields.Str()
    metadata = fields.Dict()
