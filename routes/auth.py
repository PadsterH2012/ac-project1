from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from models import User, db
from models.auth import User
from . import routes

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

@routes.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        current_user.email = request.form['email']
        db.session.commit()
        flash('Your settings have been updated.', 'success')
        return redirect(url_for('routes.settings'))
    return render_template("settings.html")
