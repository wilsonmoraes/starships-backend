import hmac
import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required

from .models.db.starships import Starship, Manufacturer, starship_manufacturer

logger = logging.getLogger(__name__)

app_routes = Blueprint("app_routes", __name__)


@app_routes.route("/api/authenticate", methods=["POST"])
def authenticate():
    """
    Authenticate user and return a JWT token.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: admin
            password:
              type: string
              example: admin
    responses:
      200:
        description: Authentication successful
        schema:
          type: object
          properties:
            token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5..."
      401:
        description: Invalid credentials
    """
    data = request.json
    username = data.get("username")
    password = data.get("password")

    valid_username = "admin"
    valid_password = "admin"

    if hmac.compare_digest(username, valid_username) and hmac.compare_digest(password, valid_password):
        access_token = create_access_token(identity=username)
        return jsonify({"token": access_token}), 200

    return jsonify({"message": "Invalid credentials"}), 401


@app_routes.route("/api/manufacturers", methods=["GET"])
@jwt_required()
def get_manufacturers():
    """
    Retrieve all manufacturers or filter by name.
    ---
    parameters:
      - name: name
        in: query
        type: string
        required: false
        description: Partial name of the manufacturer to filter by.
    responses:
      200:
        description: List of manufacturers
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: Kuat Drive Yards
    """
    name_filter = request.args.get("name")
    query = Manufacturer.query

    if name_filter:
        query = query.filter(Manufacturer.name.ilike(f"%{name_filter}%"))

    manufacturers = query.all()
    result = [{"id": m.id, "name": m.name} for m in manufacturers]
    return jsonify(result)


@app_routes.route("/api/starships", methods=["GET"])
@jwt_required()
def get_starships():
    """
    Retrieve all starships or filter by manufacturer.
    ---
    parameters:
      - name: manufacturer_id
        in: query
        type: integer
        required: false
        description: ID of the manufacturer to filter starships by.
    responses:
      200:
        description: List of starships
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: Star Destroyer
              model:
                type: string
                example: Imperial I-class Star Destroyer
              manufacturer:
                type: array
                items:
                  type: string
                example: ["Kuat Drive Yards"]
              class:
                type: string
                example: Star Destroyer
              length:
                type: float
                example: 1600
    """
    manufacturer_id = request.args.get("manufacturer_id")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    query = Starship.query

    if manufacturer_id:
        query = query.join(starship_manufacturer).filter(
            starship_manufacturer.c.manufacturer_id == int(manufacturer_id)
        )

    total_items = query.count()
    starships = query.offset((page - 1) * limit).limit(limit).all()

    result = {
        "starships": [
            {
                "id": s.id,
                "name": s.name,
                "model": s.model,
                "manufacturer": [m.name for m in s.manufacturers],
                "class": s.starship_class,
                "length": s.length,
            }
            for s in starships
        ],
        "total_items": total_items,
    }
    return jsonify(result)


@app_routes.route("/api/starships/<starship_id>", methods=["GET"])
@jwt_required()
def get_starship_detail(starship_id):
    """
    Retrieve detailed information for a specific starship.
    ---
    parameters:
      - name: starship_id
        in: path
        type: integer
        required: true
        description: ID of the starship to retrieve details for.
    responses:
      200:
        description: Starship details
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: Star Destroyer
            model:
              type: string
              example: Imperial I-class Star Destroyer
            starship_class:
              type: string
              example: Star Destroyer
            cost_in_credits:
              type: float
              example: 150000000
            length:
              type: float
              example: 1600
            crew:
              type: string
              example: 47060
            passengers:
              type: string
              example: 0
            hyperdrive_rating:
              type: float
              example: 2.0
            cargo_capacity:
              type: float
              example: 100000
            manufacturers:
              type: array
              items:
                type: string
              example: ["Kuat Drive Yards"]
    """
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
