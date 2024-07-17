from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    provider_type = db.Column(db.String(20), nullable=False)
    api_key = db.Column(db.String(120), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"Provider('{self.provider_type}', '{self.model}')"
