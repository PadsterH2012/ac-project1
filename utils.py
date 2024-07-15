import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app

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
