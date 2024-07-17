from flask import flash, redirect, url_for
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from models import User, db

def register_user(username, email, password):
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        flash('Username or email already exists.', 'error')
        return False
    else:
        new_user = User(username=username, email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash('Registered successfully. Please log in.', 'success')
        return True

def login_user_auth(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        flash('Logged in successfully.', 'success')
        return True
    else:
        flash('Invalid username or password.', 'error')
        return False

@login_required
def logout_user_auth():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('routes.index'))
