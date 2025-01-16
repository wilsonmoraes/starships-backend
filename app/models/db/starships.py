from app import db


class Manufacturer(db.Model):
    __tablename__ = "manufacturers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    starships = db.relationship(
        "StarshipManufacturer", back_populates="manufacturer", cascade="all, delete-orphan"
    )


class Starship(db.Model):
    __tablename__ = "starships"

    id = db.Column(db.Integer, primary_key=True)
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
        "StarshipManufacturer", back_populates="starship", cascade="all, delete-orphan"
    )


class StarshipManufacturer(db.Model):
    __tablename__ = "starship_manufacturers"

    id = db.Column(db.Integer, primary_key=True)
    starship_id = db.Column(db.Integer, db.ForeignKey("starships.id"), nullable=False)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey("manufacturers.id"), nullable=False)

    starship = db.relationship("Starship", back_populates="manufacturers")
    manufacturer = db.relationship("Manufacturer", back_populates="starships")
