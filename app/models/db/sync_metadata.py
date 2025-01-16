from datetime import datetime

from app import db


class SyncMetadata(db.Model):
    __tablename__ = "sync_metadata"

    id = db.Column(db.Integer, primary_key=True)
    entity = db.Column(db.String, nullable=False, unique=True)
    last_synced = db.Column(db.DateTime, default=datetime.min, nullable=False)
