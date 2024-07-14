from app import app
from models import User
from flask import jsonify, unquote, render_template  # Updated import statement

@app.route("/", methods=["GET"])
def welcome():
    return render_template("index.html")

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])
