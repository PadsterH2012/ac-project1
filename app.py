from flask import Flask, request, jsonify, render_template
from models import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db.init_app(app)

# Import routes after app is created to avoid circular imports
from routes import *


if __name__ == "__main__":
    app.run(debug=True)
