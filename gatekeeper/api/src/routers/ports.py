from flask import Blueprint, request, jsonify
from schemas.port_schema import (
    PortReserveSchema,
    PortWithBindingInstanceSchema,
    PortBindingWithInstanceSchema,
    PortParamsSchema,
    PortReleaseSchema,
)
from services.port_service import (
    get_instance,
    reserve_free_port_for_instance,
    reserve_port_range_for_instance,
    release_port_by_number,
    list_ports_with_bindings,
    release_port_by_range,
)

ports_bp = Blueprint("ports", __name__)


@ports_bp.route("/ports/reserve", methods=["POST"])
def reserve_port():
    data = request.get_json()
    errors = PortReserveSchema().validate(data)
    if errors:
        return jsonify(errors), 400

    instance = get_instance(data["instance_id"])
    if not instance:
        return jsonify({"error": "Instance not found"}), 404

    port_range = data.get("range")
    if port_range:
        reserved_ports = reserve_port_range_for_instance(instance, port_range)
        if not reserved_ports:
            return jsonify({"error": "No available port range"}), 409

        return PortBindingWithInstanceSchema().dump(reserved_ports), 201
    else:
        reserved_port = reserve_free_port_for_instance(instance)
        if not reserved_port:
            return jsonify({"error": "No available ports"}), 409
        return PortBindingWithInstanceSchema().dump(reserved_port), 201


@ports_bp.route("/ports/release", methods=["POST"])
def release_port_range():
    data = request.get_json()
    errors = PortReleaseSchema().validate(data)
    if errors:
        return jsonify(errors), 400

    start_port = data.get("start_port")
    end_port = data.get("end_port")
    port_number = data.get("port_number")
    instance_id = data.get("instance_id")


    if port_number:
        instance, error = release_port_by_number(port_number, instance_id)
    else:
        instance, error = release_port_by_range(start_port, end_port, instance_id)

    if error:
        return jsonify({"error": error}), 404 if "not found" in error else 400

    return PortBindingWithInstanceSchema().dump(instance), 200


@ports_bp.route("/ports", methods=["GET"])
def list_ports():
    params = request.args
    errors = PortParamsSchema().validate(params)
    if errors:
        return jsonify(errors), 400
    ports = list_ports_with_bindings(params)
    return PortWithBindingInstanceSchema(many=True).dump(ports)

