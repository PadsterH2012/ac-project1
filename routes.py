from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session, send_file
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from models import User, Project, Agent, Provider, db
from flask_oauthlib.client import OAuth
from backup_restore import backup_data, restore_data
import tempfile
from datetime import datetime
import json
import requests
from ollama_connection import connect_to_ollama
from utils import save_avatar, get_avatar_url

routes = Blueprint('routes', __name__)
oauth = OAuth()

google = None
facebook = None

def init_oauth(app):
    global google, facebook
    if not hasattr(oauth, 'app'):
        oauth.init_app(app)

    if google is None:
        google = oauth.remote_app(
            'google',
            consumer_key=app.config['GOOGLE_CONSUMER_KEY'],
            consumer_secret=app.config['GOOGLE_CONSUMER_SECRET'],
            request_token_params={
                'scope': 'email'
            },
            base_url='https://www.googleapis.com/oauth2/v1/',
            request_token_url=None,
            access_token_method='POST',
            access_token_url='https://accounts.google.com/o/oauth2/token',
            authorize_url='https://accounts.google.com/o/oauth2/auth',
        )

    if facebook is None:
        facebook = oauth.remote_app(
            'facebook',
            consumer_key=app.config['FACEBOOK_APP_ID'],
            consumer_secret=app.config['FACEBOOK_APP_SECRET'],
            request_token_params={'scope': 'email'},
            base_url='https://graph.facebook.com',
            request_token_url=None,
            access_token_url='/oauth/access_token',
            authorize_url='https://www.facebook.com/dialog/oauth'
        )

def init_app(app):
    init_oauth(app)
    app.register_blueprint(routes)

@routes.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return render_template("dashboard.html")
    if request.method == "POST":
        return login()
    return render_template("index.html")

@routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists.', 'error')
        else:
            new_user = User(username=username, email=email, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            flash('Registered successfully. Please log in.', 'success')
            return redirect(url_for('routes.index'))
    return render_template("register.html")

@routes.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        flash('Logged in successfully.', 'success')
        return redirect(url_for('routes.index'))
    else:
        flash('Invalid username or password.', 'error')
        return redirect(url_for('routes.index'))

@routes.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('routes.index'))

@routes.route("/projects")
@login_required
def projects():
    user_projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template("projects.html", projects=user_projects)

@routes.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Handle form submission
        current_user.email = request.form['email']
        db.session.commit()
        flash('Your settings have been updated.', 'success')
        return redirect(url_for('routes.settings'))
    return render_template("settings.html")

@routes.route("/backup", methods=['POST'])
@login_required
def backup():
    print("Backup route called")  # Debug print
    print(f"Request Content-Type: {request.content_type}")  # Debug print
    print(f"Request data: {request.data}")  # Debug print
    
    backup_options = []
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    print(f"Parsed data: {data}")  # Debug print
    
    if data.get('backup_projects'):
        backup_options.append('projects')
    if data.get('backup_agents'):
        backup_options.append('agents')
    if data.get('backup_providers'):
        backup_options.append('providers')
    
    backup_type = ','.join(backup_options) if backup_options else 'all'
    
    print(f"Calling backup_data with user_id: {current_user.id}, backup_type: {backup_type}")  # Debug print
    backup_data_json = backup_data(current_user.id, backup_type)
    
    backup_data_dict = json.loads(backup_data_json)
    if 'error' in backup_data_dict:
        return jsonify({"error": backup_data_dict['error']}), 404
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        temp_file.write(backup_data_json)
        temp_file_path = temp_file.name
    
    # Generate a filename for the download
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"incubator_backup_{timestamp}.json"
    
    print(f"Sending file: {filename}")  # Debug print
    
    # Send the file
    return send_file(temp_file_path, as_attachment=True, download_name=filename, max_age=0)

@routes.route("/restore", methods=['POST'])
@login_required
def restore():
    if 'restore_file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('routes.settings'))
    
    file = request.files['restore_file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('routes.settings'))
    
    if file:
        # Read the file content
        backup_data_json = file.read().decode('utf-8')
        
        try:
            # Restore the data
            restore_data(current_user.id, backup_data_json)
            flash('Data restored successfully', 'success')
        except Exception as e:
            flash(f'Error restoring data: {str(e)}', 'error')
        
        return redirect(url_for('routes.settings'))

@routes.route("/agent_settings", methods=["GET", "POST"])
@login_required
def agent_settings():
    providers = Provider.query.filter_by(user_id=current_user.id).all()
    if request.method == "POST":
        name = request.form.get('name')
        role = request.form.get('role')
        provider_id = request.form.get('provider_id')
        temperature = request.form.get('temperature')
        system_prompt = request.form.get('system_prompt')

        new_agent = Agent(
            name=name,
            role=role,
            provider_id=provider_id,
            temperature=temperature,
            system_prompt=system_prompt,
            user_id=current_user.id
        )

        # Handle avatar upload
        if 'avatar' in request.files:
            avatar_file = request.files['avatar']
            avatar_filename = save_avatar(avatar_file)
            if avatar_filename:
                new_agent.avatar = avatar_filename

        db.session.add(new_agent)
        db.session.commit()

        flash('Agent added successfully!', 'success')
        return redirect(url_for('routes.agent_settings'))

    agents = Agent.query.filter_by(user_id=current_user.id).all()
    return render_template("agent_settings.html", providers=providers, agents=agents)

@routes.route("/provider_settings")
@login_required
def provider_settings():
    providers = Provider.query.filter_by(user_id=current_user.id).all()
    return render_template("provider_settings.html", providers=providers)

@routes.route("/add_provider", methods=["POST"])
@login_required
def add_provider():
    provider_type = request.form.get('provider_type')
    api_key = request.form.get('api_key')
    model = request.form.get('model')
    url = request.form.get('url')

    new_provider = Provider(
        user_id=current_user.id,
        provider_type=provider_type,
        api_key=api_key,
        model=model,
        url=url if provider_type == 'ollama' else None
    )

    db.session.add(new_provider)
    db.session.commit()

    flash('Provider added successfully!', 'success')
    return redirect(url_for('routes.provider_settings'))

@routes.route("/edit_provider/<int:provider_id>", methods=["GET", "POST"])
@login_required
def edit_provider(provider_id):
    provider = Provider.query.get_or_404(provider_id)
    if provider.user_id != current_user.id:
        flash('You do not have permission to edit this provider.', 'error')
        return redirect(url_for('routes.provider_settings'))
    
    if request.method == "POST":
        provider.provider_type = request.form.get('provider_type')
        provider.api_key = request.form.get('api_key')
        provider.model = request.form.get('model')
        provider.url = request.form.get('url') if provider.provider_type == 'ollama' else None
        db.session.commit()
        flash('Provider updated successfully!', 'success')
        return redirect(url_for('routes.provider_settings'))
    
    return render_template("edit_provider.html", provider=provider)

@routes.route("/delete_provider/<int:provider_id>", methods=["POST"])
@login_required
def delete_provider(provider_id):
    provider = Provider.query.get_or_404(provider_id)
    if provider.user_id != current_user.id:
        flash('You do not have permission to delete this provider.', 'error')
        return redirect(url_for('routes.provider_settings'))
    db.session.delete(provider)
    db.session.commit()
    flash('Provider deleted successfully!', 'success')
    return redirect(url_for('routes.provider_settings'))

# Add all other route handlers here
# Make sure to update all url_for calls to include 'routes.' prefix
# For example: url_for('index') should become url_for('routes.index')

@routes.route("/continue_project/<int:project_id>")
@login_required
def continue_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('You do not have permission to access this project.', 'error')
        return redirect(url_for('routes.projects'))
    # Add your logic for continuing the project here
    return render_template("chat_interface.html", project=project)

@routes.route("/create_project", methods=["GET", "POST"])
@login_required
def create_project():
    if request.method == "POST":
        title = request.form.get('title')
        description = request.form.get('description')
        new_project = Project(title=title, description=description, user_id=current_user.id)
        db.session.add(new_project)
        db.session.commit()
        flash('Project created successfully!', 'success')
        return redirect(url_for('routes.projects'))
    return render_template("create_project.html")

@routes.route("/delete_project/<int:project_id>", methods=["POST"])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('You do not have permission to delete this project.', 'error')
        return redirect(url_for('routes.projects'))
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('routes.projects'))

@routes.route("/edit_project/<int:project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('You do not have permission to edit this project.', 'error')
        return redirect(url_for('routes.projects'))
    
    if request.method == "POST":
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('routes.projects'))
    
    return render_template("edit_project.html", project=project)

@routes.route("/edit_agent/<int:agent_id>", methods=["GET", "POST"])
@login_required
def edit_agent(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    if agent.user_id != current_user.id:
        flash('You do not have permission to edit this agent.', 'error')
        return redirect(url_for('routes.agent_settings'))
    
    providers = Provider.query.filter_by(user_id=current_user.id).all()
    
    if request.method == "POST":
        agent.name = request.form.get('name')
        agent.role = request.form.get('role')
        agent.provider_id = request.form.get('provider_id')
        agent.temperature = float(request.form.get('temperature'))
        agent.system_prompt = request.form.get('system_prompt')
        db.session.commit()
        flash('Agent updated successfully!', 'success')
        return redirect(url_for('routes.agent_settings'))
    
    return render_template("edit_agent.html", title="Edit Agent", agent=agent, providers=providers)

@routes.route("/delete_agent_from_settings/<int:agent_id>", methods=["POST"])
@login_required
def delete_agent_from_settings(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    if agent.user_id != current_user.id:
        flash('You do not have permission to delete this agent.', 'error')
        return redirect(url_for('routes.agent_settings'))
    
    db.session.delete(agent)
    db.session.commit()
    flash('Agent deleted successfully!', 'success')
    return redirect(url_for('routes.agent_settings'))

@routes.route("/chat", methods=["POST"])
@login_required
def chat():
    try:
        message = request.json.get('message')
        project_id = request.json.get('project_id')
        print(f"Received message: {message}")  # Log received message
        
        # Get the current user's AI agent
        planner_agent = Agent.query.filter_by(user_id=current_user.id, role="AI Agent Project Planner").first()
        
        if not planner_agent:
            print(f"Missing AI agent for user {current_user.id}")  # Log error
            return jsonify({"error": "Missing AI agent for the current user"}), 404
        
        # Get the provider for the agent
        planner_provider = Provider.query.get(planner_agent.provider_id)
        
        if not planner_provider:
            print(f"Missing provider for agent {planner_agent.id}")  # Log error
            return jsonify({"error": "Missing provider for the AI agent"}), 404
        
        # Prepare the prompt
        planner_prompt = f"{planner_agent.system_prompt}\n\nHuman: {message}\n\nAI:"
        print(f"Prepared prompt: {planner_prompt[:100]}...")  # Log prepared prompt (truncated)
        
        # Make request to the AI provider
        planner_response = get_ai_response(planner_provider, planner_prompt)
        
        if planner_response:
            print(f"Received AI response: {planner_response[:100]}...")  # Log AI response (truncated)
            # Create a journal entry
            journal_entry = f"User: {message}\n\nPlanner: {planner_response[:100]}..."
            
            # Update the project journal
            project = Project.query.get(project_id)
            if project:
                project.journal = (project.journal or "") + "\n\n" + journal_entry
                db.session.commit()
            else:
                print(f"Project not found: {project_id}")  # Log if project is not found
                return jsonify({"error": f"Project not found: {project_id}"}), 404
            
            return jsonify({
                "planner_response": planner_response,
                "journal_entry": journal_entry,
                "planner_name": planner_agent.name,
                "planner_role": planner_agent.role,
                "planner_avatar": get_avatar_url(planner_agent.avatar)
            })
        else:
            print("Failed to get response from AI provider")  # Log error
            return jsonify({"error": "Failed to get response from AI provider"}), 500
    except Exception as e:
        print(f"An error occurred: {str(e)}")  # Log the specific error
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@routes.route("/clear_journal", methods=["POST"])
@login_required
def clear_journal():
    project_id = request.json.get('project_id')
    project = Project.query.get(project_id)
    if project and project.user_id == current_user.id:
        project.journal = ""
        db.session.commit()
        return jsonify({"success": True, "message": "Journal cleared successfully"})
    return jsonify({"success": False, "message": "Failed to clear journal"}), 404

def get_ai_response(provider, prompt):
    if provider.provider_type == 'ollama':
        print(f"Connecting to Ollama at {provider.url}")  # Log connection attempt
        print(f"Using model: {provider.model}")  # Log model being used
        response_data = connect_to_ollama(provider.url, provider.model, prompt)
        
        print(f"Response data: {response_data}")  # Log full response data
        
        if response_data:
            ai_response = response_data.get('response', '')
            if not ai_response and response_data.get('done_reason') == 'load':
                print("AI model is still loading")  # Log loading status
                return "The AI model is still loading. Please try again in a moment."
            print(f"Received AI response: {ai_response[:100]}...")  # Log (truncated) AI response
            return ai_response
        else:
            print("Failed to get response from AI provider")  # Log error
            return None
    else:
        print(f"Unsupported AI provider: {provider.provider_type}")  # Log error
        return None
