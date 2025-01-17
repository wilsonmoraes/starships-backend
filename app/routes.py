import logging

import requests
from flask import Blueprint, render_template, request, redirect, url_for, jsonify

from .auth import authenticate_user, login_user, logout_user, is_authenticated
from .models.db.starships import Starship, Manufacturer, starship_manufacturer

logger = logging.getLogger(__name__)

app_routes = Blueprint("app_routes", __name__)


@app_routes.route("/", methods=["GET", "POST"])
def login():
    import os
    print("Template Folder:", os.path.join(os.getcwd(), "templates"))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if authenticate_user(username, password):
            login_user(username)
            return redirect(url_for("app_routes.dashboard"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app_routes.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("app_routes.login"))


@app_routes.route("/dashboard")
def dashboard():
    if not is_authenticated():
        return redirect(url_for("app_routes.login"))

    manufacturer_filter = request.args.get("manufacturer")

    try:
        # Fetch manufacturers
        manufacturers_response = requests.get(url_for("app_routes.get_manufacturers", _external=True))
        manufacturers_response.raise_for_status()
        manufacturers = manufacturers_response.json()

        # Fetch starships with optional manufacturer filter
        starships_url = url_for("app_routes.get_starships", _external=True)
        if manufacturer_filter:
            starships_url = f"{starships_url}?manufacturer_id={manufacturer_filter}"

        starships_response = requests.get(starships_url)
        starships_response.raise_for_status()
        detailed_starships = starships_response.json()

    except requests.RequestException as e:
        logger.error(f"Error fetching data from API: {e}")
        manufacturers = []
        detailed_starships = []

    return render_template(
        "dashboard.html",
        starships=detailed_starships,
        manufacturers=manufacturers,
        selected_manufacturer=manufacturer_filter  # Passa o ID selecionado
    )


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
        "manufacturers": [m.manufacturer.name for m in starship.manufacturers],
    }
    return jsonify(result)
