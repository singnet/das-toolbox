from database.db_connection import db
from datetime import datetime, timezone


class Port(db.Model):
    __tablename__ = 'port'

    id = db.Column(db.Integer, primary_key=True)
    port_number = db.Column(db.Integer, unique=True, nullable=False)
    is_reserved = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)

    bindings = db.relationship("PortBinding", back_populates="port")

    def __repr__(self):
        return f"<Port {self.port_number}>"


class Instance(db.Model):
    __tablename__ = 'instance'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    meta = db.Column('metadata', db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)

    bindings = db.relationship("PortBinding", back_populates="instance")

    def __repr__(self):
        return f"<Instance {self.name}>"


class PortBinding(db.Model):
    __tablename__ = 'port_binding'

    id = db.Column(db.Integer, primary_key=True)
    port_id = db.Column(db.Integer, db.ForeignKey('port.id'), nullable=False)
    instance_id = db.Column(db.Integer, db.ForeignKey('instance.id'), nullable=False)
    bound_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)

    port = db.relationship("Port", back_populates="bindings")
    instance = db.relationship("Instance", back_populates="bindings")

    __table_args__ = (
        db.UniqueConstraint('port_id', 'released_at', name='uq_port_active_binding'),
    )

    def __repr__(self):
        return f"<PortBinding port={self.port_id} instance={self.instance_id}>"
