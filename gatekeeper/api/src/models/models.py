from database.db_connection import db
from datetime import datetime, timezone

port_binding_ports = db.Table(
    "port_binding_ports",
    db.Column(
        "port_binding_id",
        db.Integer,
        db.ForeignKey("port_binding.id"),
        primary_key=True,
    ),
    db.Column("port_id", db.Integer, db.ForeignKey("port.id"), primary_key=True),
)


class Port(db.Model):
    __tablename__ = "port"

    id = db.Column(db.Integer, primary_key=True)
    port_number = db.Column(db.Integer, unique=True, nullable=False)
    is_reserved = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )

    bindings = db.relationship(
        "PortBinding",
        secondary=port_binding_ports,
        back_populates="ports",
    )

    def __repr__(self):
        return f"<Port {self.port_number}>"


class Instance(db.Model):
    __tablename__ = "instance"

    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    meta = db.Column(db.JSON, nullable=True)
    created_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        nullable=False,
    )

    bindings = db.relationship("PortBinding", back_populates="instance")

    def __repr__(self):
        return f"<Instance {self.name}>"


class PortBinding(db.Model):
    __tablename__ = "port_binding"

    id = db.Column(db.Integer, primary_key=True)
    instance_id = db.Column(
        db.String(255),
        db.ForeignKey("instance.id"),
        nullable=False,
    )
    bound_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        nullable=False,
    )
    released_at = db.Column(db.DateTime, nullable=True)
    start_port = db.Column(db.Integer, nullable=False)
    end_port = db.Column(db.Integer, nullable=False)

    ports = db.relationship(
        "Port",
        secondary=port_binding_ports,
        back_populates="bindings",
    )
    instance = db.relationship("Instance", back_populates="bindings")

    def __repr__(self):
        return f"<PortBinding {self.start_port}:{self.end_port} instance={self.instance_id}>"
