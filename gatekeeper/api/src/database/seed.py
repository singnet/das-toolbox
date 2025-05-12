from database.db_connection import db
from models.models import Port

def run_port_seeder():
    ports = [Port(port_number=p) for p in range(8000, 10000)]
    db.session.add_all(ports)
    db.session.flush()

def run_seeder():
    print("Seeding...")
    run_port_seeder()
    print("Seed completed successfully.")

