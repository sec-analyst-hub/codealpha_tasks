import json
import os
import re
import shutil
import sqlite3
import subprocess

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "")  # from environment
ph = PasswordHasher()  # Argon2 password hashing
DB = "users.db"


def get_db():
    return sqlite3.connect(DB)


@app.route("/login", methods=["POST"])
def login():
    user = request.form["username"]
    row = get_db().execute(
        "SELECT password FROM users WHERE username = ?", (user,)  # parameterized
    ).fetchone()
    if row:
        try:
            ph.verify(row[0], request.form["password"])
            return "Welcome"
        except VerifyMismatchError:
            return "Denied", 401
    return "Denied", 401


@app.route("/ping")
def ping():
    host = request.args.get("host", "")
    if not re.fullmatch(r"[A-Za-z0-9.\-]{1,253}", host):  # allow-list validation
        return "Invalid host", 400
    ping_bin = shutil.which("ping")  # full path of the executable
    if ping_bin is None:
        return "ping not available", 500
    out = subprocess.run(  # noqa: S603  (no shell, validated input)
        [ping_bin, "-c", "1", host], capture_output=True, text=True, timeout=5
    )
    return out.stdout


@app.route("/hello")
def hello():
    name = request.args.get("name", "")
    return f"<h1>Hello {escape(name)}</h1>"  # output escaping


@app.route("/load", methods=["POST"])
def load():
    return str(json.loads(request.data))  # JSON instead of pickle


# /calc removed: eval() on user input cannot be made safe


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1")
