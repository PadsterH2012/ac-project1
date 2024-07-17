from flask import jsonify, send_file, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models.models import User
from services.backup.backup_restore import backup_data, restore_data
import tempfile
from datetime import datetime
import json
from . import routes

@routes.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@routes.route("/backup", methods=['POST'])
@login_required
def backup():
    print("Backup route called")  # Debug print
    print(f"Request Content-Type: {request.content_type}")  # Debug print
    print(f"Request data: {request.data}")  # Debug print
    
    backup_options = []
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    print(f"Parsed data: {data}")  # Debug print
    
    if data.get('backup_projects'):
        backup_options.append('projects')
    if data.get('backup_agents'):
        backup_options.append('agents')
    if data.get('backup_providers'):
        backup_options.append('providers')
    
    backup_type = ','.join(backup_options) if backup_options else 'all'
    
    print(f"Calling backup_data with user_id: {current_user.id}, backup_type: {backup_type}")  # Debug print
    backup_data_json = backup_data(current_user.id, backup_type)
    
    backup_data_dict = json.loads(backup_data_json)
    if 'error' in backup_data_dict:
        return jsonify({"error": backup_data_dict['error']}), 404
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        temp_file.write(backup_data_json)
        temp_file_path = temp_file.name
    
    # Generate a filename for the download
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"incubator_backup_{timestamp}.json"
    
    print(f"Sending file: {filename}")  # Debug print
    
    # Send the file
    return send_file(temp_file_path, as_attachment=True, download_name=filename, max_age=0)

@routes.route("/restore", methods=['POST'])
@login_required
def restore():
    if 'restore_file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('routes.settings'))
    
    file = request.files['restore_file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('routes.settings'))
    
    if file:
        # Read the file content
        backup_data_json = file.read().decode('utf-8')
        
        try:
            # Parse the backup data
            backup_data = json.loads(backup_data_json)
            
            # Render a template with the backup contents for selection
            return render_template('restore_selection.html', backup_data=backup_data)
        except Exception as e:
            flash(f'Error parsing backup file: {str(e)}', 'error')
        
        return redirect(url_for('routes.settings'))

@routes.route("/perform_restore", methods=['POST'])
@login_required
def perform_restore():
    selected_items = request.form.getlist('restore_items')
    backup_data = request.form.get('backup_data')
    
    try:
        # Restore the selected data
        restore_data(current_user.id, backup_data, selected_items)
        flash('Data restored successfully', 'success')
    except Exception as e:
        flash(f'Error restoring data: {str(e)}', 'error')
    
    return redirect(url_for('routes.settings'))
