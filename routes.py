from models import User, Project, Agent, db
from flask import jsonify, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_oauthlib.client import OAuth
from flask_login import login_user, login_required, logout_user, current_user

oauth = OAuth()

google = oauth.remote_app(
    'google',
    consumer_key='your_google_consumer_key',
    consumer_secret='your_google_consumer_secret',
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

facebook = oauth.remote_app(
    'facebook',
    consumer_key='your_facebook_app_id',
    consumer_secret='your_facebook_app_secret',
    request_token_params={'scope': 'email'},
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth'
)

def init_app(app):
    oauth.init_app(app)

    @app.route('/oauth-login/<provider>')
    def oauth_login(provider):
        if provider == 'google':
            return google.authorize(callback=url_for('oauth_callback', provider=provider, _external=True))
        elif provider == 'facebook':
            return facebook.authorize(callback=url_for('oauth_callback', provider=provider, _external=True))
        else:
            flash('Unsupported OAuth provider', 'error')
            return redirect(url_for('index'))


    @app.route('/oauth-callback/<provider>')
    def oauth_callback(provider):
        if provider == 'google':
            resp = google.authorized_response()
            if resp is None or resp.get('access_token') is None:
                flash('Access denied: reason={} error={}'.format(
                    request.args['error_reason'],
                    request.args['error_description']
                ), 'error')
                return redirect(url_for('index'))
            session['google_token'] = (resp['access_token'], '')
            me = google.get('userinfo')
            user_email = me.data['email']
            user_id = me.data['id']
        elif provider == 'facebook':
            resp = facebook.authorized_response()
            if resp is None or 'access_token' not in resp:
                flash('Access denied: reason={} error={}'.format(
                    request.args['error_reason'],
                    request.args['error_description']
                ), 'error')
                return redirect(url_for('index'))
            session['facebook_token'] = (resp['access_token'], '')
            me = facebook.get('/me?fields=id,email')
            user_email = me.data['email']
            user_id = me.data['id']
        else:
            flash('Unsupported OAuth provider', 'error')
            return redirect(url_for('index'))

        user = User.query.filter_by(email=user_email).first()
        if user is None:
            user = User(username=user_email.split('@')[0], email=user_email, oauth_provider=provider, oauth_id=user_id)
            db.session.add(user)
            db.session.commit()

        session['user_id'] = user.id
        flash('Logged in successfully.', 'success')
        return redirect(url_for('index'))
    @app.route("/", methods=["GET", "POST"])
    def index():
        if current_user.is_authenticated:
            return render_template("dashboard.html")
        if request.method == "POST":
            return login()
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
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
                return redirect(url_for('index'))
        return render_template("register.html")

    @app.route("/users", methods=["GET"])
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
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('index'))

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'success')
        return redirect(url_for('index'))

    @app.route("/settings", methods=["GET"])
    @login_required
    def settings():
        return render_template("settings.html")

    @app.route("/settings/provider", methods=["GET"])
    @login_required
    def provider_settings():
        providers = Provider.query.filter_by(user_id=current_user.id).all()
        return render_template("provider_settings.html", providers=providers)

    @app.route("/settings/provider/add", methods=["POST"])
    @login_required
    def add_provider():
        provider_type = request.form.get('provider_type')
        api_key = request.form.get('api_key')
        model = request.form.get('model')
        url = request.form.get('url') if provider_type == 'ollama' else None

        new_provider = Provider(
            user_id=current_user.id,
            provider_type=provider_type,
            api_key=api_key,
            model=model,
            url=url
        )
        db.session.add(new_provider)
        db.session.commit()
        flash('Provider added successfully!', 'success')
        return redirect(url_for('provider_settings'))

    @app.route("/settings/provider/<int:provider_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_provider(provider_id):
        provider = Provider.query.get_or_404(provider_id)
        if provider.user_id != current_user.id:
            flash('You do not have permission to edit this provider.', 'error')
            return redirect(url_for('provider_settings'))

        if request.method == "POST":
            provider.api_key = request.form.get('api_key')
            provider.model = request.form.get('model')
            if provider.provider_type == 'ollama':
                provider.url = request.form.get('url')
            db.session.commit()
            flash('Provider updated successfully!', 'success')
            return redirect(url_for('provider_settings'))

        return render_template("edit_provider.html", provider=provider)

    @app.route("/settings/provider/<int:provider_id>/delete", methods=["POST"])
    @login_required
    def delete_provider(provider_id):
        provider = Provider.query.get_or_404(provider_id)
        if provider.user_id != current_user.id:
            flash('You do not have permission to delete this provider.', 'error')
            return redirect(url_for('provider_settings'))

        db.session.delete(provider)
        db.session.commit()
        flash('Provider deleted successfully!', 'success')
        return redirect(url_for('provider_settings'))

    @app.route("/settings/agent", methods=["GET", "POST"])
    @login_required
    def agent_settings():
        if request.method == "POST":
            agent_settings = request.form.to_dict()
            current_user.agent_settings = agent_settings
            db.session.commit()
            flash('Agent settings updated successfully!', 'success')
            return redirect(url_for('agent_settings'))
        return render_template("agent_settings.html", settings=current_user.agent_settings)

    @app.route("/projects")
    @login_required
    def projects():
        user_projects = Project.query.filter_by(user_id=current_user.id).all()
        return render_template("projects.html", projects=user_projects)

    @app.route("/projects/create", methods=["GET", "POST"])
    @login_required
    def create_project():
        if request.method == "POST":
            title = request.form.get('title')
            description = request.form.get('description')
            new_project = Project(title=title, description=description, user_id=current_user.id)
            db.session.add(new_project)
            db.session.commit()
            flash('Project created successfully!', 'success')
            return redirect(url_for('projects'))
        return render_template("create_project.html")

    @app.route("/projects/<int:project_id>/delete", methods=["POST"])
    @login_required
    def delete_project(project_id):
        project = Project.query.get_or_404(project_id)
        if project.user_id != current_user.id:
            flash('You do not have permission to delete this project.', 'error')
            return redirect(url_for('projects'))
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted successfully!', 'success')
        return redirect(url_for('projects'))

    @app.route("/projects/<int:project_id>/continue")
    @login_required
    def continue_project(project_id):
        project = Project.query.get_or_404(project_id)
        if project.user_id != current_user.id:
            flash('You do not have permission to access this project.', 'error')
            return redirect(url_for('projects'))
        return render_template("continue_project.html", project=project)

    @app.route("/projects/<int:project_id>/manage_agents", methods=["GET", "POST"])
    @login_required
    def manage_agents(project_id):
        project = Project.query.get_or_404(project_id)
        if project.user_id != current_user.id:
            flash('You do not have permission to access this project.', 'error')
            return redirect(url_for('projects'))
    
        if request.method == "POST":
            agent_name = request.form.get('agent_name')
            agent_role = request.form.get('agent_role')
            new_agent = Agent(name=agent_name, role=agent_role, user_id=current_user.id, project_id=project.id)
            db.session.add(new_agent)
            db.session.commit()
            flash('Agent added successfully!', 'success')
            return redirect(url_for('manage_agents', project_id=project.id))
    
        return render_template("manage_agents.html", project=project)

    @app.route("/projects/<int:project_id>/agents/<int:agent_id>/delete", methods=["POST"])
    @login_required
    def delete_agent(project_id, agent_id):
        agent = Agent.query.get_or_404(agent_id)
        if agent.user_id != current_user.id:
            flash('You do not have permission to delete this agent.', 'error')
            return redirect(url_for('manage_agents', project_id=project_id))
        db.session.delete(agent)
        db.session.commit()
        flash('Agent deleted successfully!', 'success')
        return redirect(url_for('manage_agents', project_id=project_id))
