from flask import Flask
from models import db
from routes import init_app as init_routes
from flask_login import LoginManager
from flask_migrate import Migrate

login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "your_secret_key_here"  # Replace with a real secret key
    app.config["GOOGLE_CONSUMER_KEY"] = "your_google_client_id"
    app.config["GOOGLE_CONSUMER_SECRET"] = "your_google_client_secret"
    app.config["FACEBOOK_APP_ID"] = "your_facebook_app_id"
    app.config["FACEBOOK_APP_SECRET"] = "your_facebook_app_secret"
    app.config['UPLOAD_FOLDER'] = 'static/avatars'
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'routes.index'
    migrate.init_app(app, db)

    # Register routes
    init_routes(app)

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()  # This line creates the database tables

    return app

@create_app().cli.command("db_migrate")
def db_migrate():
    from migrations import add_provider_id_to_agent
    add_provider_id_to_agent.upgrade()