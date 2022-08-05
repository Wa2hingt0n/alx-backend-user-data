#!/usr/bin/env python3
""" Creates a flask app """
from flask import Flask, jsonify, request, abort
from auth import Auth


app = Flask(__name__)
AUTH = Auth()


@app.route("/", strict_slashes=False)
def index() -> str:
    """ Returns a payload message """
    return jsonify({"message": "Bienvenue"})


@app.route("/users", strict_slashes=False, methods=["POST"])
def users() -> str:
    """ User registration endpoint """
    email = request.form.get("email")
    password = request.form.get("password")
    try:
        AUTH.register_user(email, password)
        return jsonify({"email": email, "message": "user created"})
    except ValueError:
        return jsonify({"message": "email already registered"}), 400


@app.route("/sessions", strict_slashes=False, methods=["POST"])
def login():
    """ If user is validated, creates a new session and stores the session ID
    as a cookie with the key 'session_id'
    """
    email = request.form.get("email")
    password = request.form.get("password")
    if not AUTH.valid_login(email, password):
        abort(401)
    session_id = AUTH.create_session(email)
    response = jsonify({"email": email, "message": "logged in"})
    response.set_cookie("session_id", session_id)
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
