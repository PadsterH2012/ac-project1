from flask import Flask
from models import db
import routes

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "your_secret_key_here"  # Replace with a real secret key
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Register routes
    routes.init_app(app)

    return app
