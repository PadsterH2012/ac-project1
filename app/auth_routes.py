from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User, db
from .auth import register_user, login_user_auth, logout_user_auth

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return render_template("dashboard.html")
    if request.method == "POST":
        return login()
    return render_template("index.html")

@auth_routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if register_user(username, email, password):
            return redirect(url_for('auth_routes.index'))
    return render_template("register.html")

@auth_routes.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if login_user_auth(username, password):
        return redirect(url_for('auth_routes.index'))
    return redirect(url_for('auth_routes.index'))

@auth_routes.route("/logout")
@login_required
def logout():
    return logout_user_auth()

@auth_routes.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        current_user.email = request.form['email']
        db.session.commit()
        flash('Your settings have been updated.', 'success')
        return redirect(url_for('auth_routes.settings'))
    return render_template("settings.html")
