from flask import Flask
from config import Config
from routers import register_routes
from database.db_connection import db
from database.seed import run_seeder

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    register_routes(app)

    with app.app_context():
        db.create_all()
        run_seeder()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
