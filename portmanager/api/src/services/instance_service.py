from models.models import Instance
from database.db_connection import db


def list_instances_service():
    return Instance.query.all()


def create_instance_service(name, metadata=None):
    instance = Instance(name=name, meta=metadata or {})
    db.session.add(instance)
    db.session.commit()
    return instance


def get_instance_service(instance_id):
    return Instance.query.get(instance_id)


def update_instance_service(instance, data):
    if "name" in data:
        instance.name = data["name"]
    if "metadata" in data:
        instance.meta = data["metadata"]
    db.session.commit()
    return instance


def delete_instance_service(instance):
    db.session.delete(instance)
    db.session.commit()
    return instance
