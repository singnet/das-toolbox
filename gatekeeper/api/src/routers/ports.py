from flask import Blueprint, request, jsonify
from schemas.port_schema import (
    PortReserveSchema,
    PortWithBindingInstanceSchema,
    PortBindingWithInstanceSchema,
    PortSchema,
    ObserverRequestSchema,
)
from services.port_service import (
    get_instance,
    reserve_free_port_for_instance,
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
    result = list_ports_with_bindings()
    return PortWithBindingInstanceSchema(many=True).jsonify(result)


@ports_bp.route("/ports/observe", methods=["POST"])
def observe_ports():
    data = request.get_json()
    errors = ObserverRequestSchema().validate(data)
    if errors:
        return jsonify(errors), 400

    ports = observe_ports_for_instance(data["instance_id"], data["ports"])
    if ports is None:
        return jsonify({"error": "Instance not found"}), 404

    return PortSchema(many=True).dump(ports)
