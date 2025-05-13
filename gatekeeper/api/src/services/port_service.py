from datetime import datetime, timezone
from database.db_connection import db
from models.models import Port, PortBinding, Instance
from sqlalchemy import select


def get_instance(instance_id):
    return Instance.query.get(instance_id)


def reserve_free_port_for_instance(instance):
    used_ports = (
        db.session.query(PortBinding.port_id)
        .filter(PortBinding.released_at.is_(None))
        .subquery()
    )
    free_port = Port.query.filter(Port.id.not_in(select(used_ports))).first()

    if not free_port:
        return None

    binding = PortBinding(port_id=free_port.id, instance_id=instance.id)
    free_port.is_reserved = True
    db.session.add(binding)
    db.session.commit()
    return binding


def release_port_by_number(port_number):
    port = Port.query.filter_by(port_number=port_number).first()
    if not port:
        return None, "Port not found"

    binding = PortBinding.query.filter_by(port_id=port.id, released_at=None).first()
    if not binding:
        return None, "Port is not currently bound"

    binding.released_at = datetime.now(timezone.utc)
    port.is_reserved = False
    db.session.commit()

    return binding, None


def list_ports_with_bindings():
    ports = Port.query.all()
    result = []

    for port in ports:
        binding = PortBinding.query.filter_by(port_id=port.id, released_at=None).first()
        if binding:
            db.session.refresh(binding)
        result.append(
            {"id": port.id, "port_number": port.port_number, "binding": binding}
        )

    return result


def observe_ports_for_instance(instance_id, used_ports):
    instance = get_instance(instance_id)
    if not instance:
        return None

    now = datetime.now(timezone.utc)
    ports = Port.query.filter(Port.port_number.in_(used_ports)).all()
    port_ids = [port.id for port in ports]

    db.session.query(PortBinding).filter(
        PortBinding.instance_id == instance_id,
        PortBinding.released_at.is_(None),
        ~PortBinding.port_id.in_(port_ids),
    ).update(
        {PortBinding.released_at: now},
        synchronize_session=False,
    )

    for port in ports:
        existing_binding = PortBinding.query.filter_by(
            port_id=port.id,
            instance_id=instance_id,
            released_at=None,
        ).first()

        if not existing_binding:
            db.session.add(
                PortBinding(port_id=port.id, instance_id=instance_id, observed_at=now)
            )

    db.session.commit()
    return ports
