from flask import session

USERS = {"admin": "admin"}  # Mock de autenticação

def authenticate_user(username, password):
    return USERS.get(username) == password

def login_user(username):
    session["user"] = username

def logout_user():
    session.pop("user", None)

def is_authenticated():
    return "user" in session
