from models import User, db
from flask import jsonify, render_template, request, flash, redirect, url_for
# Import unquote from urllib.parse if needed
# from urllib.parse import unquote

def init_app(app):
    @app.route("/", methods=["GET"])
    def welcome():
        return render_template("index.html")

    @app.route("/users", methods=["GET"])
    def get_users():
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])

    @app.route("/login", methods=["POST"])
    def login():
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            flash('Logged in successfully.', 'success')
            return redirect(url_for('welcome'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))
