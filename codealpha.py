import sqlite3
import hashlib
import os
import pickle
import subprocess
from flask import Flask, request, render_template_string

app = Flask(__name__)
SECRET_KEY = "admin123"                      # hardcoded secret
DB = "users.db"


def get_db():
    return sqlite3.connect(DB)


@app.route("/login", methods=["POST"])
def login():
    user = request.form["username"]
    pwd = hashlib.md5(request.form["password"].encode()).hexdigest()   # weak hash
    query = "SELECT * FROM users WHERE username='" + user + "' AND password='" + pwd + "'"
    row = get_db().execute(query).fetchone()  # SQL injection
    return "Welcome" if row else "Denied"


@app.route("/ping")
def ping():
    host = request.args.get("host")
    return subprocess.check_output("ping -c 1 " + host, shell=True)   # command injection


@app.route("/hello")
def hello():
    name = request.args.get("name", "")
    return render_template_string("<h1>Hello " + name + "</h1>")      # XSS / SSTI


@app.route("/load", methods=["POST"])
def load():
    data = pickle.loads(request.data)         # insecure deserialization
    return str(data)


@app.route("/calc")
def calc():
    return str(eval(request.args.get("expr")))   # code injection


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")       # debug mode on
