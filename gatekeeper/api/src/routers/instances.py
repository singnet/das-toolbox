from flask import Blueprint, request, jsonify
from schemas.instance_schema import (
    InstanceCreateSchema,
    InstanceUpdateSchema,
    InstanceResponseSchema,
)
from services.instance_service import (
    list_instances_service,
    create_instance_service,
    get_instance_service,
    update_instance_service,
    delete_instance_service,
)

instances_bp = Blueprint("instances", __name__)


@instances_bp.route("/instances", methods=["GET"])
def list_instances():
    instances = list_instances_service()

    return InstanceResponseSchema(many=True).dump(instances), 200


@instances_bp.route("/instances/<string:instance_id>", methods=["GET"])
def get_instance_by_id(instance_id):
    instance = get_instance_service(instance_id)
    if not instance:
        return {"error": "Instance not found"}, 404

    return InstanceResponseSchema().dump(instance), 200


@instances_bp.route("/instances", methods=["POST"])
def create_instance():
    data = request.get_json()
    errors = InstanceCreateSchema().validate(data)
    if errors:
        return jsonify(errors), 400

    try:
        instance = create_instance_service(
            data["instance_id"],
            data["name"],
            data.get("meta"),
        )
        return InstanceResponseSchema().dump(instance), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 409

    except Exception as e:
        return (
            jsonify({"error": "An unexpected error occurred.", "details": str(e)}),
            500,
        )


@instances_bp.route("/instances/<int:instance_id>", methods=["PUT"])
def update_instance(instance_id):
    instance = get_instance_service(instance_id)
    if not instance:
        return jsonify({"error": "Instance not found"}), 404

    data = request.get_json()
    errors = InstanceUpdateSchema().validate(data)
    if errors:
        return jsonify(errors), 400

    updated_instance = update_instance_service(instance, data)
    return InstanceResponseSchema().dump(updated_instance), 200


@instances_bp.route("/instances/<int:instance_id>", methods=["DELETE"])
def delete_instance(instance_id):
    instance = get_instance_service(instance_id)
    if not instance:
        return jsonify({"error": "Instance not found"}), 404

    deleted_instance = delete_instance_service(instance)
    return InstanceResponseSchema().dump(deleted_instance), 200
