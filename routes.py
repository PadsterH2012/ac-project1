from models import User, db
from flask import jsonify, render_template, request, flash, redirect, url_for
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

    @app.route("/settings", methods=["GET", "POST"])
    @login_required
    def settings():
        if request.method == "POST":
            email = request.form.get('email')
            if email and email != current_user.email:
                current_user.email = email
                db.session.commit()
                flash('Settings updated successfully!', 'success')
            return redirect(url_for('settings'))
        return render_template("settings.html")
