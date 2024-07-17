from flask import Blueprint
from app.auth_routes import auth_routes
from app.chat_routes import chat_routes
from app.project_routes import project_routes

routes = Blueprint('routes', __name__)

def init_app(app):
    app.register_blueprint(routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(chat_routes)
    app.register_blueprint(project_routes)

# Keep the backup and restore routes here
@routes.route("/backup", methods=['POST'])
@login_required
def backup():
    # ... (keep the existing backup route implementation)
    pass

@routes.route("/restore", methods=['POST'])
@login_required
def restore():
    # ... (keep the existing restore route implementation)
    pass

# Keep the agent and provider settings routes here
@routes.route("/agent_settings", methods=["GET", "POST"])
@login_required
def agent_settings():
    # ... (keep the existing agent_settings route implementation)
    pass

@routes.route("/provider_settings")
@login_required
def provider_settings():
    # ... (keep the existing provider_settings route implementation)
    pass

@routes.route("/add_provider", methods=["POST"])
@login_required
def add_provider():
    # ... (keep the existing add_provider route implementation)
    pass

@routes.route("/edit_provider/<int:provider_id>", methods=["GET", "POST"])
@login_required
def edit_provider(provider_id):
    # ... (keep the existing edit_provider route implementation)
    pass

@routes.route("/delete_provider/<int:provider_id>", methods=["POST"])
@login_required
def delete_provider(provider_id):
    # ... (keep the existing delete_provider route implementation)

@routes.route("/edit_agent/<int:agent_id>", methods=["GET", "POST"])
@login_required
def edit_agent(agent_id):
    # ... (keep the existing edit_agent route implementation)

@routes.route("/delete_agent_from_settings/<int:agent_id>", methods=["POST"])
@login_required
def delete_agent_from_settings(agent_id):
    # ... (keep the existing delete_agent_from_settings route implementation)
