from flask import Blueprint, render_template, request, redirect, url_for

from .auth import authenticate_user, login_user, logout_user, is_authenticated

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

    # Obter naves detalhadas
    detailed_starships = []

    # Filtrar por fabricante, se necessário
    if manufacturer_filter:
        detailed_starships = [s for s in detailed_starships if manufacturer_filter in s["manufacturer"]]

    # Obter lista de fabricantes únicos
    manufacturers = sorted(set(ship["manufacturer"] for ship in detailed_starships))

    return render_template(
        "dashboard.html",
        starships=detailed_starships,
        manufacturers=manufacturers,
        selected_manufacturer=manufacturer_filter
    )
