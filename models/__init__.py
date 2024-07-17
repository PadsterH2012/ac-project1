from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

from .auth import User
from .project import Project
from .agent import Agent
from .provider import Provider

# Ensure all models are imported here to avoid circular imports
