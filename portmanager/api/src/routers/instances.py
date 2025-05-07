from flask import Blueprint, request, jsonify
from database.db_connection import db
from models.models import Instance
from schemas.instance_schema import InstanceCreateSchema, InstanceResponseSchema, InstanceUpdateSchema

instances_bp = Blueprint('instances', __name__)


@instances_bp.route('/instances', methods=['GET'])
def list_instances():
    instances = Instance.query.all()

    return InstanceResponseSchema(many=True).jsonify(instances), 200

@instances_bp.route('/instances', methods=['POST'])
def create_instance():
    data = request.get_json()
    errors = InstanceCreateSchema().validate(data)
    if errors:
        return jsonify(errors), 400

    name = data['name']
    metadata = data.get('metadata', {})

    instance = Instance(name=name, meta=metadata)
    db.session.add(instance)
    db.session.commit()

    return InstanceResponseSchema().jsonify(instance), 201

@instances_bp.route('/instances/<int:instance_id>', methods=['PUT'])
def update_instance(instance_id):
    instance = Instance.query.get(instance_id)
    if not instance:
        return jsonify({"error": "Instance not found"}), 404

    data = request.get_json()
    errors = InstanceUpdateSchema().validate(data)
    if errors:
        return jsonify(errors), 400

    if 'name' in data:
        instance.name = data['name']
    if 'metadata' in data:
        instance.meta = data['metadata']

    db.session.commit()
    return InstanceResponseSchema().jsonify(instance), 200


@instances_bp.route('/instances/<int:instance_id>', methods=['DELETE'])
def delete_instance(instance_id):
    instance = Instance.query.get(instance_id)
    if not instance:
        return jsonify({"error": "Instance not found"}), 404

    db.session.delete(instance)
    db.session.commit()
    return InstanceResponseSchema().jsonify(instance), 200
