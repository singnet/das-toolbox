from flask import Flask
from config import Config
from database import db
from routes import bp
from seed import create_port_pool

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()
        create_port_pool(8000, 10000)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
