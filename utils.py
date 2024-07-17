import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app, url_for

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def save_avatar(file):
    if file and allowed_file(file.filename):
        # Generate a random filename
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Resize and save the image
        with Image.open(file) as img:
            img.thumbnail((128, 128))  # Resize to 128x128 pixels max
            img.save(filepath, optimize=True, quality=85)  # Optimize and slightly reduce quality
        
        return filename
    return None
def get_avatar_url(filename):
    if filename:
        return url_for('static', filename=f'avatars/{filename}')
    return url_for('static', filename='avatars/default_agent.jpg')
import os
from flask import current_app, jsonify
import logging

logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_avatar(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        return filename
    return None

def get_avatar_url(filename):
    if filename:
        return url_for('static', filename=f'avatars/{filename}')
    return url_for('static', filename='avatars/default_agent.jpg')

def handle_error(error_message, status_code=400):
    logger.error(error_message)
    return jsonify({"error": error_message}), status_code

def log_info(message):
    logger.info(message)

def log_debug(message):
    logger.debug(message)
