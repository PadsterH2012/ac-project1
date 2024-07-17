from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from app.error_handlers import register_error_handlers
from app.logging_config import configure_logging

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    from app.config import Config
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_routes.index'
    migrate.init_app(app, db)

    # Register routes
    from app.routes import init_app as init_routes
    init_routes(app)

    # Register error handlers
    register_error_handlers(app)

    # Configure logging
    configure_logging(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.database_models import User
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()  # This line creates the database tables

    return app
