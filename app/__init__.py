import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    template_dir = os.path.join(os.path.dirname(__file__), '../templates')
    app = Flask(__name__, template_folder=template_dir)

    app.secret_key = "supersecretkey"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///starships.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = True

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import app_routes
    app.register_blueprint(app_routes)

    @app.cli.command("create-db")
    def create_db():
        """Create the database tables."""
        with app.app_context():
            db.create_all()
        print("Database tables created.")

    return app
