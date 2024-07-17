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
from flask import jsonify

@app.route('/chat', methods=['POST'])
def chat():
    user_id = current_user.id if current_user.is_authenticated else None
    message = request.json.get('message')

    # Get AI agents for the user
    planner_agent = Agent.query.filter_by(user_id=user_id, role='Project Planner').first()
    writer_agent = Agent.query.filter_by(user_id=user_id, role='Project Writer').first()

    if not planner_agent or not writer_agent:
        return jsonify({
            'error': 'Missing AI agents for the user. Please create the required agents.'
        }), 400

    # Process the message with AI agents and generate responses
    planner_response = process_with_ai(planner_agent, message)
    writer_response = process_with_ai(writer_agent, message)

    # Create a journal entry
    journal_entry = f"User: {message}\nPlanner: {planner_response}\nWriter: {writer_response}"

    return jsonify({
        'planner_response': planner_response,
        'writer_response': writer_response,
        'journal_entry': journal_entry,
        'planner_name': planner_agent.name,
        'planner_role': planner_agent.role,
        'planner_avatar': planner_agent.avatar_url,
        'writer_name': writer_agent.name,
        'writer_role': writer_agent.role,
        'writer_avatar': writer_agent.avatar_url
    })

def process_with_ai(agent, message):
    # Implement your AI processing logic here
    # This is a placeholder implementation
    return f"AI {agent.role} response to: {message}"
from models import Agent, db

def create_default_agents(user_id):
    default_agents = [
        {
            'name': 'Default Project Planner',
            'role': 'Project Planner',
            'system_prompt': 'You are an AI assistant specialized in project planning.',
            'avatar_url': '/static/avatars/default_agent.jpg'
        },
        {
            'name': 'Default Project Writer',
            'role': 'Project Writer',
            'system_prompt': 'You are an AI assistant specialized in project documentation and writing.',
            'avatar_url': '/static/avatars/default_agent.jpg'
        }
    ]

    for agent_data in default_agents:
        agent = Agent.query.filter_by(user_id=user_id, role=agent_data['role']).first()
        if not agent:
            new_agent = Agent(user_id=user_id, **agent_data)
            db.session.add(new_agent)
    
    db.session.commit()

@app.route('/chat', methods=['POST'])
def chat():
    user_id = current_user.id if current_user.is_authenticated else None
    if not user_id:
        return jsonify({'error': 'User not authenticated'}), 401

    create_default_agents(user_id)  # Ensure default agents exist

    # ... rest of the chat function ...
