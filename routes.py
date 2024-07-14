from app import app
from models import User
from flask import jsonify, render_template
# Import unquote from urllib.parse if needed
# from urllib.parse import unquote

@app.route("/", methods=["GET"])
def welcome():
    return render_template("index.html")

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])
