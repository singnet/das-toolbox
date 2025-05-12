from marshmallow import Schema, fields, validate


class PortSchema(Schema):
    id = fields.Int()
    port_number = fields.Int()


class InstanceSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    meta = fields.Dict()


class PortBindingSchema(Schema):
    id = fields.Int()
    port = fields.Nested(PortSchema)
    released_at = fields.DateTime(allow_none=True)


class InstanceWithPortBindingSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    meta = fields.Dict()
    bindings = fields.Nested(PortBindingSchema, many=True)


class PortReserveSchema(Schema):
    instance_id = fields.Str(required=True)


class PortBindingWithInstanceSchema(Schema):
    id = fields.Int()
    released_at = fields.DateTime(allow_none=True)
    instance = fields.Nested(InstanceSchema)


class PortWithBindingInstanceSchema(Schema):
    id = fields.Int()
    port_number = fields.Int()
    binding = fields.Nested(PortBindingWithInstanceSchema, allow_none=True)


class ObserverRequestSchema(Schema):
    instance_id = fields.Str(required=True)
    ports = fields.List(fields.Int(), required=True, validate=validate.Length(min=1))
