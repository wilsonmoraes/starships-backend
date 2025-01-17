import logging

from flask import Blueprint, request, jsonify

from .models.db.starships import Starship, Manufacturer, starship_manufacturer

logger = logging.getLogger(__name__)

app_routes = Blueprint("app_routes", __name__)


@app_routes.route("/api/manufacturers", methods=["GET"])
def get_manufacturers():
    name_filter = request.args.get("name")
    query = Manufacturer.query

    if name_filter:
        query = query.filter(Manufacturer.name.ilike(f"%{name_filter}%"))

    manufacturers = query.all()
    result = [{"id": m.id, "name": m.name} for m in manufacturers]
    return jsonify(result)


@app_routes.route("/api/starships", methods=["GET"])
def get_starships():
    manufacturer_id = request.args.get("manufacturer_id")
    query = Starship.query

    if manufacturer_id:
        query = query.join(starship_manufacturer).filter(
            starship_manufacturer.c.manufacturer_id == int(manufacturer_id))

    starships = query.all()
    result = [
        {
            "id": s.id,
            "name": s.name,
            "model": s.model,
            "manufacturer": [m.name for m in s.manufacturers],
            "class": s.starship_class,
            "length": s.length,
        }
        for s in starships
    ]
    return jsonify(result)


@app_routes.route("/api/starships/<starship_id>", methods=["GET"])
def get_starship_detail(starship_id):
    starship = Starship.query.get_or_404(starship_id)
    result = {
        "id": starship.id,
        "name": starship.name,
        "model": starship.model,
        "starship_class": starship.starship_class,
        "cost_in_credits": starship.cost_in_credits,
        "length": starship.length,
        "crew": starship.crew,
        "passengers": starship.passengers,
        "max_atmosphering_speed": starship.max_atmosphering_speed,
        "hyperdrive_rating": starship.hyperdrive_rating,
        "MGLT": starship.MGLT,
        "cargo_capacity": starship.cargo_capacity,
        "consumables": starship.consumables,
        "created_at": starship.created_at,
        "edited_at": starship.edited_at,
        "url": starship.url,
        "manufacturers": [m.name for m in starship.manufacturers],
    }
    return jsonify(result)
