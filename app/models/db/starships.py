from sqlalchemy import Table, Integer, ForeignKey, Column

from app.models.db import db


starship_manufacturer = Table(
    "starship_manufacturer",
    db.Model.metadata,
    Column("starship_id", Integer, ForeignKey("starships.id"), primary_key=True),
    Column("manufacturer_id", Integer, ForeignKey("manufacturers.id"), primary_key=True),
)

class Starship(db.Model):
    __tablename__ = "starships"

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    model = db.Column(db.String, nullable=False)
    starship_class = db.Column(db.String, nullable=False)
    cost_in_credits = db.Column(db.BigInteger, nullable=True)
    length = db.Column(db.Float, nullable=True)
    crew = db.Column(db.Integer, nullable=True)
    passengers = db.Column(db.Integer, nullable=True)
    max_atmosphering_speed = db.Column(db.String, nullable=True)
    hyperdrive_rating = db.Column(db.Float, nullable=True)
    MGLT = db.Column(db.Integer, nullable=True)
    cargo_capacity = db.Column(db.BigInteger, nullable=True)
    consumables = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    edited_at = db.Column(db.DateTime, nullable=False)
    url = db.Column(db.String, nullable=False)

    manufacturers = db.relationship(
        "Manufacturer",
        secondary="starship_manufacturer",
        back_populates="starships",
    )

class Manufacturer(db.Model):
    __tablename__ = "manufacturers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    starships = db.relationship(
        "Starship",
        secondary="starship_manufacturer",
        back_populates="manufacturers",
    )
