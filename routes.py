from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from models import User, Project, Agent, Provider, db
from flask_oauthlib.client import OAuth

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
        return redirect(url_for('routes.dashboard'))
    if request.method == "POST":
        return login()
    return render_template("index.html")

@routes.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

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

    new_provider = Provider(
        user_id=current_user.id,
        provider_type=provider_type,
        api_key=api_key,
        model=model
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

@routes.route("/check_login")
def check_login():
    return jsonify({"logged_in": current_user.is_authenticated})

@routes.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json()
    message = data.get('message')
    project_id = data.get('project_id')

    if not message or not project_id:
        return jsonify({"error": "Missing message or project ID"}), 400

    # Get the current user's AI agent
    agent = Agent.query.filter_by(user_id=current_user.id).first()
    
    if not agent:
        return jsonify({"error": "Missing AI agent for the current user"}), 404

    # Get the provider for the agent
    provider = Provider.query.get(agent.provider_id)
    
    if not provider:
        return jsonify({"error": "Missing provider for the AI agent"}), 404

    # Prepare the prompt
    prompt = f"{agent.system_prompt}\n\nHuman: {message}\n\nAI:"

    # Make request to the AI provider
    # This is a placeholder. You need to implement the actual API call.
    ai_response = "This is a placeholder response from the AI."

    # Update the project journal
    project = Project.query.get(project_id)
    if project:
        if project.user_id != current_user.id:
            return jsonify({"error": "You do not have permission to access this project"}), 403
        
        project.journal = (project.journal or "") + f"\nUser: {message}\nAI: {ai_response}"
        db.session.commit()
    else:
        return jsonify({"error": f"Project not found: {project_id}"}), 404

    return jsonify({"response": ai_response})
