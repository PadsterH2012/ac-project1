from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models
from .project import Project
from .agent import Agent
from .provider import Provider
from .auth import User

# Other relationships are defined in their respective models
