from flask import Flask
from models import db

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
    db.init_app(app)

    # Import routes after app is created to avoid circular imports
    with app.app_context():
        from routes import *

    return app
