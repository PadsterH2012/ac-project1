from flask import Flask
from models import db
import routes

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
    db.init_app(app)

    # Register routes
    routes.init_app(app)

    return app
