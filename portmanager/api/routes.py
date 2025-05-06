from flask import Blueprint, request, jsonify
from models import Port
from database import db
from auth import token_required

bp = Blueprint('api', __name__)

@bp.route('/ports/reserve', methods=['POST'])
@token_required
def reserve_port():
    data = request.json
    port = data.get('port')
    machine = data.get('machine')
    service = data.get('service', '')

    existing = Port.query.filter_by(port=port, machine=machine, status='reserved').first()
    if existing:
        return jsonify({"error": "Port already reserved"}), 409

    new_port = Port(port=port, machine=machine, service=service, status='reserved')
    db.session.add(new_port)
    db.session.commit()
    return jsonify({"message": "Port reserved", "id": new_port.id}), 201

@bp.route('/ports/release', methods=['POST'])
@token_required
def release_port():
    data = request.json
    port = data.get('port')
    machine = data.get('machine')

    entry = Port.query.filter_by(port=port, machine=machine, status='reserved').first()
    if not entry:
        return jsonify({"error": "Port not found"}), 404

    db.session.delete(entry)
    db.session.commit()

    return jsonify({"message": "Port released"})


@bp.route('/ports', methods=['GET'])
@token_required
def list_ports():
    ports = Port.query.all()
    return jsonify([{
        "port": p.port,
        "machine": p.machine,
        "service": p.service,
        "status": p.status,
        "created_at": p.created_at.isoformat()
    } for p in ports])

@bp.route('/ports/report', methods=['POST'])
@token_required
def report_ports():
    data = request.json
    active_ports = data.get('active_ports', [])
    machine = data.get('machine')

    conflicts = []
    for port in active_ports:
        registered = Port.query.filter_by(port=port, machine=machine, status='reserved').first()
        if not registered:
            conflicts.append(port)

    return jsonify({
        "message": "Report received",
        "conflicts": conflicts
    })
