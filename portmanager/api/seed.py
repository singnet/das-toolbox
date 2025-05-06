from models import Port
from database import db

def create_port_pool(start_port, end_port):
    for port in range(start_port, end_port + 1):
        existing = Port.query.filter_by(port=port, status='available').first()
        if not existing:
            new_port = Port(port=port, status='available')
            db.session.add(new_port)

    db.session.commit()

