from marshmallow import Schema, fields, validate


class PortSchema(Schema):
    id = fields.Int()
    port_number = fields.Int()


class InstanceSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    meta = fields.Dict()


class PortReserveSchema(Schema):
    instance_id = fields.Str(required=True)


class PortBindingWithInstanceSchema(Schema):
    id = fields.Int()
    released_at = fields.DateTime(allow_none=True)
    instance = fields.Nested(InstanceSchema)
    port = fields.Nested(PortSchema)


class PortWithBindingInstanceSchema(Schema):
    id = fields.Int()
    port_number = fields.Int()
    binding = fields.Nested(PortBindingWithInstanceSchema, allow_none=True)


class ObserverRequestSchema(Schema):
    instance_id = fields.Str(required=True)
    ports = fields.List(fields.Int(), required=True, validate=validate.Length(min=1))
