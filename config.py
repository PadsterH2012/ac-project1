import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_CONSUMER_KEY = os.environ.get('GOOGLE_CONSUMER_KEY')
    GOOGLE_CONSUMER_SECRET = os.environ.get('GOOGLE_CONSUMER_SECRET')
    FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
    FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')
    UPLOAD_FOLDER = 'app/app/static/avatars'
