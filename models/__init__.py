from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .auth import User
from .project import Project
from .agent import Agent
from .provider import Provider

# Set up relationships
User.projects = db.relationship('Project', backref='user', lazy=True)
User.agents = db.relationship('Agent', backref='user', lazy=True)
User.providers = db.relationship('Provider', backref='user', lazy=True)

Agent.provider = db.relationship('Provider', backref='agents')
Agent.project = db.relationship('Project', back_populates='agents')

Project.agents = db.relationship('Agent', back_populates='project', lazy=True)
