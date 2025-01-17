import os

from apscheduler.schedulers.background import BackgroundScheduler
from flasgger import Swagger
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.models.db import init_db
from app.sync.sync_job import SyncJob


def create_app():
    template_dir = os.path.join(os.path.dirname(__file__), '../templates')
    app = Flask(__name__, template_folder=template_dir)

    app.secret_key = "supersecretkey"

    app.config["SCHEDULER_API_ENABLED"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = True

    init_db(app=app)

    from app.routes import app_routes
    app.register_blueprint(app_routes)
    CORS(app)

    Swagger(app)
    JWTManager(app)
    return app


scheduler = BackgroundScheduler()
scheduler.start()

# scheduler.add_job(
#     id="sync_starships",
#     func=SyncJob.sync_starships,
#     trigger="interval",
#     seconds=10,
#     replace_existing=True,
# )
