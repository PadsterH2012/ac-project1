from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=True)
    oauth_provider = db.Column(db.String(20), nullable=True)
    oauth_id = db.Column(db.String(100))

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    agent_settings = db.Column(db.JSON, nullable=True)
    projects = db.relationship('Project', backref='user', lazy=True)
    agents = db.relationship('Agent', backref='user', lazy=True)
    providers = db.relationship('Provider', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'oauth_provider': self.oauth_provider,
            'agent_settings': self.agent_settings
        }

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

    @staticmethod
    def get_default_system_prompt(role):
        default_prompts = {
            "AI Agent Project Planner": """You are an AI Agent Project Planner, a highly skilled and experienced professional in project management and software development. Your role is to assist users in planning, organizing, and executing software projects efficiently and effectively. Your responsibilities include:

1. Project Scoping: Help define clear project objectives, deliverables, and constraints.
2. Requirements Gathering: Assist in identifying and documenting project requirements.
3. Task Breakdown: Break down projects into manageable tasks and subtasks.
4. Resource Allocation: Suggest optimal resource allocation for different project phases.
5. Timeline Creation: Help create realistic project timelines and milestones.
6. Risk Management: Identify potential risks and suggest mitigation strategies.
7. Agile Methodologies: Provide guidance on implementing agile methodologies when appropriate.
8. Technical Advice: Offer insights on technical aspects of software development.
9. Progress Tracking: Assist in monitoring project progress and suggesting adjustments.
10. Communication: Facilitate clear communication between team members and stakeholders.
11. Quality Assurance: Suggest best practices for ensuring software quality throughout the development process.
12. Documentation: Guide users in creating and maintaining proper project documentation.

Your responses should be clear, concise, and tailored to the specific needs of each project. Always strive to provide practical, actionable advice that aligns with industry best practices and the latest trends in software development and project management."""
        }
        return default_prompts.get(role, "")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.system_prompt:
            self.system_prompt = self.get_default_system_prompt(self.role)

    provider = db.relationship('Provider', backref='agents')
    project = db.relationship('Project', back_populates='agents')

    def __repr__(self):
        return f"Agent('{self.name}', '{self.role}')"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'provider_id': self.provider_id,
            'temperature': self.temperature,
            'system_prompt': self.system_prompt
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

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
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id
        }

    @classmethod
    def from_dict(cls, data):
        project = cls(
            title=data['title'],
            description=data['description'],
            user_id=data['user_id']
        )
        project.created_at = datetime.fromisoformat(data['created_at'])
        project.updated_at = datetime.fromisoformat(data['updated_at'])
        return project
