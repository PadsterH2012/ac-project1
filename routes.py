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

@routes.route("/settings")
@login_required
def settings():
    return render_template("settings.html")

@routes.route("/agent_settings")
@login_required
def agent_settings():
    # Placeholder for agent settings
    return render_template("agent_settings.html")

@routes.route("/provider_settings")
@login_required
def provider_settings():
    providers = Provider.query.filter_by(user_id=current_user.id).all()
    return render_template("provider_settings.html", providers=providers)

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
    return render_template("continue_project.html", project=project)

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
