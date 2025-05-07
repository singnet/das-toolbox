from flask import Blueprint, request, jsonify
from datetime import timezone, datetime
from database.db_connection import db
from models.models import Port, PortBinding, Instance
from schemas.port_schema import (
    InstanceWithPortBindingSchema,
    PortReserveSchema,
    PortWithBindingInstanceSchema,
)

ports_bp = Blueprint("ports", __name__)


@ports_bp.route("/ports/reserve", methods=["POST"])
def reserve_port():
    data = request.get_json()
    errors = PortReserveSchema().validate(data)
    if errors:
        return jsonify(errors), 400

    instance_id = data["instance_id"]
    instance = Instance.query.get(instance_id)
    if not instance:
        return jsonify({"error": "Instance not found"}), 404

    used_ports = (
        db.session.query(PortBinding.port_id)
        .filter(PortBinding.released_at == None)
        .subquery()
    )
    free_port = Port.query.filter(Port.id.not_in(used_ports)).first()

    if not free_port:
        return jsonify({"error": "No available ports"}), 409

    binding = PortBinding(
        port_id=free_port.id,
        instance_id=instance.id,
    )
    free_port.is_reserved = True
    db.session.add(binding)
    db.session.commit()

    instance.bindings = [binding]
    return InstanceWithPortBindingSchema().jsonify(instance), 201


@ports_bp.route("/ports/<int:port_number>/release", methods=["POST"])
def release_port(port_number):
    port = Port.query.filter_by(port_number=port_number).first()
    if not port:
        return jsonify({"error": "Port not found"}), 404

    binding = PortBinding.query.filter_by(port_id=port.id, released_at=None).first()
    if not binding:
        return jsonify({"error": "Port is not currently bound"}), 400

    binding.released_at = datetime.now(timezone.utc)
    port.is_reserved = False
    db.session.commit()

    instance = Instance.query.get(binding.instance_id)
    instance.bindings = [binding]
    return InstanceWithPortBindingSchema().jsonify(instance), 200


@ports_bp.route("/ports", methods=["GET"])
def list_ports():
    ports = Port.query.all()
    result = []

    for port in ports:
        binding = PortBinding.query.filter_by(port_id=port.id, released_at=None).first()
        if binding:
            db.session.refresh(binding)
        result.append(
            {"id": port.id, "port_number": port.port_number, "binding": binding}
        )

    return PortWithBindingInstanceSchema(many=True).jsonify(result)
