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
    range = fields.Int(required=False)


class PortBindingWithInstanceSchema(Schema):
    id = fields.Int()
    start_port = fields.Int()
    end_port = fields.Int()
    bound_at = fields.DateTime()
    released_at = fields.DateTime(allow_none=True)
    instance = fields.Nested(InstanceSchema)
    ports = fields.Nested(PortSchema, many=True)


class PortWithBindingInstanceSchema(Schema):
    id = fields.Int()
    port_number = fields.Int()
    bindings = fields.Nested(
        PortBindingWithInstanceSchema,
        many=True,
        allow_none=True,
    )


class PortParamsSchema(Schema):
    instance_id = fields.Str(required=False)
    is_reserved = fields.Boolean()


class ObserverRequestSchema(Schema):
    instance_id = fields.Str(required=True)
    ports = fields.List(
        fields.Int(),
        required=True,
        validate=validate.Length(min=0),
    )
