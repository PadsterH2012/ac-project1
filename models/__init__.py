from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .auth import User
from .project import Project
from .agent import Agent
from .provider import Provider

# Relationships are now defined in their respective models
