from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models
from .auth import User
from .project import Project
from .agent import Agent
from .provider import Provider

# Define relationships after all models are imported
User.projects = db.relationship('Project', back_populates='user', lazy=True)
User.agents = db.relationship('Agent', backref='user', lazy=True)
User.providers = db.relationship('Provider', backref='user', lazy=True)

# Other relationships are defined in their respective models
