from marshmallow import Schema, fields, validate, validates_schema, ValidationError


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

class PortReleaseSchema(Schema):
    port_number = fields.Int(required=False, allow_none=True)
    start_port = fields.Int(required=False, allow_none=True)
    end_port = fields.Int(required=False, allow_none=True)
    instance_id = fields.Str(required=False, allow_none=True)

    @validates_schema
    def validate_port_fields(self, data, **kwargs):
        if not data.get("port_number"):
            if data.get("start_port") is None or data.get("end_port") is None:
                raise ValidationError(
                    "Either 'port_number' or both 'start_port' and 'end_port' must be provided.",
                    field_name="start_port"
                )


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
