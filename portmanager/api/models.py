from database import db
from datetime import datetime

class Port(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    port = db.Column(db.Integer, nullable=False)
    machine = db.Column(db.String(128), nullable=True)
    service = db.Column(db.String(128))
    status = db.Column(db.String(32), nullable=False, default='available') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
