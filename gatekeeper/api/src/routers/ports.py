from flask import Blueprint, request, jsonify
from schemas.port_schema import (
    PortReserveSchema,
    PortWithBindingInstanceSchema,
    PortBindingWithInstanceSchema,
    PortSchema,
    ObserverRequestSchema,
    PortParamsSchema,
)
from services.port_service import (
    get_instance,
    reserve_free_port_for_instance,
    reserve_port_range_for_instance,
    release_port_by_number,
    list_ports_with_bindings,
    observe_ports_for_instance,
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

        start_port = reserved_ports[0].port_number
        end_port = reserved_ports[-1].port_number
        return jsonify({"range": f"{start_port}:{end_port}"}), 201
    else:
        reserved_port = reserve_free_port_for_instance(instance)
        if not reserved_port:
            return jsonify({"error": "No available ports"}), 409
        return PortBindingWithInstanceSchema().dump(reserved_port), 201


@ports_bp.route("/ports/<int:port_number>/release", methods=["POST"])
def release_port(port_number):
    instance, error = release_port_by_number(port_number)
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


@ports_bp.route("/ports/observe", methods=["POST"])
def observe_ports():
    data = request.get_json()
    errors = ObserverRequestSchema().validate(data)
    if errors:
        return jsonify(errors), 400

    ports = observe_ports_for_instance(
        data["instance_id"],
        data["ports"],
    )
    if ports is None:
        return jsonify({"error": "Instance not found"}), 404

    return PortSchema(many=True).dump(ports)
