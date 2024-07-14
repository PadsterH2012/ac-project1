from flask import Flask
from models import db
import routes
from flask_login import LoginManager
from flask_migrate import Migrate

login_manager = LoginManager()
migrate = Migrate()

def create_app():
    from models import User  # Add this import at the top of the file

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "your_secret_key_here"  # Replace with a real secret key
    app.config["GOOGLE_ID"] = "your_google_client_id"
    app.config["GOOGLE_SECRET"] = "your_google_client_secret"
    app.config["FACEBOOK_APP_ID"] = "your_facebook_app_id"
    app.config["FACEBOOK_APP_SECRET"] = "your_facebook_app_secret"
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'index'
    migrate.init_app(app, db)

    # Register routes
    routes.init_app(app)

    return app

    @app.cli.command("db_migrate")
    def db_migrate():
        with app.app_context():
            from migrations import add_provider_id_to_agent
            add_provider_id_to_agent.upgrade()

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    return app
