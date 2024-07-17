from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=True)
    oauth_provider = db.Column(db.String(20), nullable=True)
    oauth_id = db.Column(db.String(100))

    agent_settings = db.Column(db.JSON, nullable=True)

    projects = db.relationship('Project', back_populates='user', lazy=True)
    agents = db.relationship('Agent', backref='user', lazy=True)
    providers = db.relationship('Provider', backref='user', lazy=True)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'oauth_provider': self.oauth_provider,
            'agent_settings': self.agent_settings
        }

    def __repr__(self):
        return f"User('{self.username}')"
