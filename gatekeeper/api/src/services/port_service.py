from datetime import datetime, timezone
from database.db_connection import db
from models.models import Port, PortBinding, Instance, port_binding_ports
from sqlalchemy import select
from config import Config


def get_instance(instance_id):
    return Instance.query.get(instance_id)


def reserve_port_range_for_instance(instance, size):
    size = int(size)

    used_ports_subquery = (
        db.session.query(port_binding_ports.c.port_id)
        .join(PortBinding, port_binding_ports.c.port_binding_id == PortBinding.id)
        .filter(PortBinding.released_at.is_(None))
        .subquery()
    )

    free_ports = (
        Port.query.filter(
            Port.id.not_in(select(used_ports_subquery)), Port.is_reserved == False
        )
        .order_by(Port.port_number)
        .all()
    )

    start_index = 0
    while start_index + size <= len(free_ports):
        window = free_ports[start_index : start_index + size]
        expected_end = window[0].port_number + size - 1
        if window[-1].port_number == expected_end:
            for port in window:
                port.is_reserved = True

            binding = PortBinding(
                instance_id=instance.id,
                start_port=window[0].port_number,
                end_port=window[-1].port_number,
            )
            db.session.add(binding)
            db.session.flush()

            binding.ports.extend(window)

            db.session.commit()
            return binding
        start_index += 1

    highest_port = (
        db.session.query(Port.port_number).order_by(Port.port_number.desc()).first()
    )
    next_port_number = (
        Config.PORT_RANGE_START if highest_port is None else highest_port[0] + 1
    )

    if next_port_number + size - 1 >= Config.PORT_RANGE_END:
        return None

    reserved_ports = []
    for i in range(size):
        port_number = next_port_number + i
        new_port = Port(port_number=port_number, is_reserved=True)
        db.session.add(new_port)
        db.session.flush()
        reserved_ports.append(new_port)

    binding = PortBinding(
        instance_id=instance.id,
        start_port=reserved_ports[0].port_number,
        end_port=reserved_ports[-1].port_number,
    )
    db.session.add(binding)
    db.session.flush()

    binding.ports.extend(reserved_ports)

    db.session.commit()
    return binding


def reserve_free_port_for_instance(instance):
    used_ports = (
        db.session.query(port_binding_ports.c.port_id)
        .join(PortBinding, port_binding_ports.c.port_binding_id == PortBinding.id)
        .filter(PortBinding.released_at.is_(None))
        .subquery()
    )

    free_port = (
        Port.query.filter(Port.id.not_in(select(used_ports)), Port.is_reserved == False)
        .order_by(Port.port_number)
        .first()
    )

    if not free_port:
        highest_port = (
            db.session.query(Port.port_number).order_by(Port.port_number.desc()).first()
        )
        next_port_number = (
            Config.PORT_RANGE_START if highest_port is None else highest_port[0] + 1
        )

        if next_port_number >= Config.PORT_RANGE_END:
            return None

        free_port = Port(port_number=next_port_number, is_reserved=False)
        db.session.add(free_port)
        db.session.commit()

    free_port.is_reserved = True
    binding = PortBinding(
        instance_id=instance.id,
        start_port=free_port.port_number,
        end_port=free_port.port_number,
        ports=[free_port],
    )

    db.session.add(binding)
    db.session.commit()

    return binding


def release_port_by_number(port_number, instance_id=None):
    port = Port.query.filter_by(port_number=port_number).first()
    if not port:
        return None, "Port not found"

    binding = PortBinding.query

    if instance_id:
        binding = binding.filter_by(instance_id=instance_id)

    binding = (
        binding.join(
            port_binding_ports,
            PortBinding.id == port_binding_ports.c.port_binding_id,
        )
        .filter(
            port_binding_ports.c.port_id == port.id,
            PortBinding.released_at.is_(None),
        )
        .first()
    )

    if not binding:
        return None, "Port is not currently bound"

    binding.released_at = datetime.now(timezone.utc)

    for bound_port in binding.ports:
        bound_port.is_reserved = False

    db.session.commit()
    return binding, None


def release_port_by_range(start_port, end_port, instance_id=None):
    if start_port > end_port:
        return None, "Start port must be less than or equal to end port"

    binding = PortBinding.query

    if instance_id:
        binding = binding.filter_by(instance_id=instance_id)

    binding = (
        binding.filter_by(
            start_port=start_port,
            end_port=end_port,
        )
        .filter(PortBinding.released_at.is_(None))
        .first()
    )

    if not binding:
        return None, f"No active binding found for range {start_port}:{end_port}"

    binding.released_at = datetime.now(timezone.utc)

    for port in binding.ports:
        port.is_reserved = False

    db.session.commit()
    return binding, None


def list_ports_with_bindings(params=None):
    if params is None:
        params = {}

    query = db.session.query(Port)

    is_reserved = params.get("is_reserved")
    if is_reserved is not None:
        query = query.filter(Port.is_reserved == bool(is_reserved))

    instance_id = params.get("instance_id")
    if instance_id is not None:
        query = (
            query.join(port_binding_ports, Port.id == port_binding_ports.c.port_id)
            .join(PortBinding, PortBinding.id == port_binding_ports.c.port_binding_id)
            .filter(
                PortBinding.instance_id == instance_id,
                PortBinding.released_at.is_(None),
            )
        )

    return query.all()


def get_or_create_ports(port_numbers):
    min_port, max_port = (
        Config.PORT_RANGE_START,
        Config.PORT_RANGE_END,
    )
    valid_ports = [p for p in port_numbers if min_port <= p <= max_port]

    if not valid_ports:
        return []

    existing_ports = Port.query.filter(Port.port_number.in_(valid_ports)).all()
    existing_map = {p.port_number: p for p in existing_ports}

    new_ports = []
    for port_number in valid_ports:
        if port_number not in existing_map:
            new_port = Port(port_number=port_number, is_reserved=False)
            db.session.add(new_port)
            new_ports.append(new_port)

    db.session.flush()

    return existing_ports + new_ports
