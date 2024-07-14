from models import User, db
from flask import jsonify, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

def init_app(app):
    @app.route("/", methods=["GET", "POST"])
    def index():
        if 'user_id' in session:
            return render_template("dashboard.html")
        if request.method == "POST":
            if "login" in request.form:
                return login()
            elif "register" in request.form:
                return register()
        return render_template("index.html")

    @app.route("/users", methods=["GET"])
    def get_users():
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])

    def login():
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('index'))

    def register():
        username = request.form.get('username')
        password = request.form.get('password')
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists.', 'error')
        else:
            new_user = User(username=username, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            flash('Registered successfully. Please log in.', 'success')
        return redirect(url_for('index'))

    @app.route("/logout")
    def logout():
        session.pop('user_id', None)
        flash('You have been logged out.', 'success')
        return redirect(url_for('index'))
