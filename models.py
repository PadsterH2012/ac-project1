from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=True)
    oauth_provider = db.Column(db.String(20), nullable=True)
    oauth_id = db.Column(db.String(120), nullable=True)
    agent_settings = db.Column(db.JSON, nullable=True)
    projects = db.relationship('Project', backref='user', lazy=True)
    agents = db.relationship('Agent', backref='user', lazy=True)
    providers = db.relationship('Provider', backref='user', lazy=True)

class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    provider_type = db.Column(db.String(20), nullable=False)
    api_key = db.Column(db.String(120), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"Provider('{self.provider_type}', '{self.model}')"

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)  # Changed to nullable
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=False)
    temperature = db.Column(db.Float, nullable=False, default=0.7)
    system_prompt = db.Column(db.Text, nullable=True)

    provider = db.relationship('Provider', backref='agents')
    project = db.relationship('Project', back_populates='agents')

    def __repr__(self):
        return f"Agent('{self.name}', '{self.role}')"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'provider': self.provider.to_dict(),
            'temperature': self.temperature,
            'system_prompt': self.system_prompt
        }

    def __repr__(self):
        return f"User('{self.username}')"

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username
        }

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    agents = db.relationship('Agent', back_populates='project', lazy=True)

    def __repr__(self):
        return f"Project('{self.title}')"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
