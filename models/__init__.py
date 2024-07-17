from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models
from .auth import User
from .project import Project
from .agent import Agent
from .provider import Provider

# Other relationships are defined in their respective models
