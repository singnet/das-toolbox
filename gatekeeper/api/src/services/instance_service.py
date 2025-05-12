from models.models import Instance
from sqlalchemy.exc import IntegrityError
from database.db_connection import db


def list_instances_service():
    return Instance.query.all()



def create_instance_service(instance_id, name, meta=None):
    instance = Instance(
        id=instance_id,
        name=name,
        meta=meta or {},
    )
    db.session.add(instance)

    try:
        db.session.commit()
        return instance
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError("Instance with this ID already exists.") from e

def get_instance_service(instance_id):
    return Instance.query.get(instance_id)


def update_instance_service(instance, data):
    if "name" in data:
        instance.name = data["name"]
    if "meta" in data:
        instance.meta = data["meta"]
    db.session.commit()
    return instance


def delete_instance_service(instance):
    db.session.delete(instance)
    db.session.commit()
    return instance
