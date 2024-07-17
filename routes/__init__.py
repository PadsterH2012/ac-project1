from flask import Blueprint
from flask_login import LoginManager

routes = Blueprint('routes', __name__)

from . import auth, projects, agents, providers, chat, misc

def init_app(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'routes.index'

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    app.register_blueprint(routes)
