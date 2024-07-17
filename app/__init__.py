from flask import Flask
from database_models import db
from .routes import init_app as init_routes
from flask_login import LoginManager
from flask_migrate import Migrate
from .config import Config
from .error_handlers import register_error_handlers
from .logging_config import configure_logging

login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'routes.index'
    migrate.init_app(app, db)

    # Register routes
    init_routes(app)

    # Register error handlers
    register_error_handlers(app)

    # Configure logging
    configure_logging(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .database_models import User
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()  # This line creates the database tables

    return app
