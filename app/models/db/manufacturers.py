from app import db


class Manufacturer(db.Model):
    __tablename__ = "manufacturers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    starships = db.relationship(
        "StarshipManufacturer", back_populates="manufacturer", cascade="all, delete-orphan"
    )
