from flask_sqlalchemy import SQLAlchemy
from services.prompt_config.prompt_config import DEFAULT_PROMPTS

db = SQLAlchemy()

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=False)
    temperature = db.Column(db.Float, nullable=False, default=0.7)
    system_prompt = db.Column(db.Text, nullable=True)
    avatar = db.Column(db.String(255), nullable=True)  # Stores the randomized avatar filename

    @staticmethod
    def get_default_system_prompt(role):
        return DEFAULT_PROMPTS.get(role, "")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.system_prompt:
            self.system_prompt = self.get_default_system_prompt(self.role)

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
