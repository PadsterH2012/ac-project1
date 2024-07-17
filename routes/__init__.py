from flask import Blueprint

routes = Blueprint('routes', __name__)

from . import auth, projects, agents, providers, chat, misc
