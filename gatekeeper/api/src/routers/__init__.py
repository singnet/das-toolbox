from .ports import ports_bp
from .instances import instances_bp

def register_routes(app):
    app.register_blueprint(ports_bp, url_prefix='/api')
    app.register_blueprint(instances_bp, url_prefix='/api')
