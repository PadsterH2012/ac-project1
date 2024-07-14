from flask import render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from models import User, Project, Agent, Provider, db
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from models import User, Project, Agent, Provider, db
from routes import google, facebook

routes = Blueprint('routes', __name__)

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

@routes.route('/oauth-login/<provider>')
def oauth_login(provider):
    if provider == 'google':
        return google.authorize(callback=url_for('routes.oauth_callback', provider=provider, _external=True))
    elif provider == 'facebook':
        return facebook.authorize(callback=url_for('routes.oauth_callback', provider=provider, _external=True))
    else:
        flash('Unsupported OAuth provider', 'error')
        return redirect(url_for('routes.index'))

@routes.route('/oauth-callback/<provider>')
def oauth_callback(provider):
    if provider == 'google':
        resp = google.authorized_response()
        if resp is None or resp.get('access_token') is None:
            flash('Access denied: reason={} error={}'.format(
                request.args['error_reason'],
                request.args['error_description']
            ), 'error')
            return redirect(url_for('routes.index'))
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
            return redirect(url_for('routes.index'))
        session['facebook_token'] = (resp['access_token'], '')
        me = facebook.get('/me?fields=id,email')
        user_email = me.data['email']
        user_id = me.data['id']
    else:
        flash('Unsupported OAuth provider', 'error')
        return redirect(url_for('routes.index'))

    user = User.query.filter_by(email=user_email).first()
    if user is None:
        user = User(username=user_email.split('@')[0], email=user_email, oauth_provider=provider, oauth_id=user_id)
        db.session.add(user)
        db.session.commit()

    session['user_id'] = user.id
    flash('Logged in successfully.', 'success')
    return redirect(url_for('routes.index'))

# Add all other route handlers from the original routes.py file here
# Make sure to update all url_for calls to include 'routes.' prefix
# For example: url_for('index') should become url_for('routes.index')
