from flask import jsonify, send_file, request, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from models.models import User, Project, Agent, Provider
from services.backup.backup_restore import backup_data, restore_data
import tempfile
from datetime import datetime
import json
import re
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
        except json.JSONDecodeError as e:
            flash(f'Error parsing backup file: {str(e)}', 'error')
        except Exception as e:
            flash(f'Error processing backup file: {str(e)}', 'error')
        
        return redirect(url_for('routes.settings'))

@routes.route("/perform_restore", methods=['POST'])
@login_required
def perform_restore():
    try:
        selected_items = request.form.getlist('restore_items')
        backup_data_str = request.form.get('backup_data')
        print(f"Received backup_data: {backup_data_str[:100]}...")  # Print first 100 chars for debugging
        print(f"Full backup_data: {backup_data_str}")  # Print the full backup data for debugging
        
        try:
            # Remove any leading/trailing whitespace
            backup_data_str = backup_data_str.strip()
            
            print(f"Raw backup data: {backup_data_str[:100]}...")  # Log raw data
            
            # Check if the string starts and ends with curly braces
            if not (backup_data_str.startswith('{') and backup_data_str.endswith('}')):
                backup_data_str = '{' + backup_data_str + '}'
            
            # Remove any extra curly braces at the beginning or end
            backup_data_str = backup_data_str.strip('{}')
            backup_data_str = '{' + backup_data_str + '}'
            
            print(f"Processed backup data: {backup_data_str[:100]}...")  # Log processed data
            
            # Attempt to parse the JSON
            backup_data = json.loads(backup_data_str)
            
            # Check if the required keys exist in the backup data
            required_keys = ['projects', 'agents', 'providers']
            for key in required_keys:
                if key not in backup_data:
                    print(f"'{key}' key not found in backup data")
                    backup_data[key] = []  # Initialize with an empty list if the key is missing
            
        except json.JSONDecodeError as json_error:
            print(f"JSON Decode Error: {str(json_error)}")
            print(f"Error at position: {json_error.pos}")
            print(f"Line number: {json_error.lineno}, Column: {json_error.colno}")
            print(f"Problematic part: {backup_data_str[max(0, json_error.pos-20):json_error.pos+20]}")
            
            # Attempt to sanitize and parse the JSON
            try:
                # Replace single quotes with double quotes
                sanitized_data = backup_data_str.replace("'", '"')
                # Ensure property names are in double quotes
                sanitized_data = re.sub(r'(\w+)(?=\s*:)', r'"\1"', sanitized_data)
                # Remove any extra commas
                sanitized_data = re.sub(r',\s*}', '}', sanitized_data)
                sanitized_data = re.sub(r',\s*]', ']', sanitized_data)
                print(f"Sanitized data: {sanitized_data[:100]}...")  # Log sanitized data
                backup_data = json.loads(sanitized_data)
                
                # Check if the required keys exist in the sanitized backup data
                for key in required_keys:
                    if key not in backup_data:
                        print(f"'{key}' key not found in sanitized backup data")
                        backup_data[key] = []  # Initialize with an empty list if the key is missing
                
            except Exception as e:
                print(f"Error after sanitization: {str(e)}")  # Log error after sanitization
                flash(f'Error parsing backup data: {str(e)}', 'error')
                return redirect(url_for('routes.settings'))
        
        # Prepare the data to restore
        data_to_restore = {
            'projects': [],
            'agents': [],
            'providers': []
        }
        
        for item in selected_items:
            item_type, item_id = item.split('_')
            item_id = int(item_id)
            
            if item_type in ['project', 'agent', 'provider']:
                items = backup_data.get(item_type + 's', [])
                item_data = next((i for i in items if i['id'] == item_id), None)
                if item_data:
                    data_to_restore[item_type + 's'].append(item_data)
                else:
                    print(f"Item {item_type} with id {item_id} not found in backup data")
        
        # Check if any data was selected for restoration
        if not any(data_to_restore.values()):
            flash('No data selected for restoration or no matching data found in the backup', 'warning')
            return redirect(url_for('routes.settings'))
        
        # Restore the selected data
        restore_data(current_user.id, json.dumps(data_to_restore))
        flash('Data restored successfully', 'success')
    except json.JSONDecodeError as e:
        flash(f'Error parsing backup data: {str(e)}', 'error')
        print(f"JSON Decode Error: {str(e)}")
        print(f"Error at position: {e.pos}")
        print(f"Line number: {e.lineno}, Column: {e.colno}")
    except Exception as e:
        flash(f'Error restoring data: {str(e)}', 'error')
        print(f"General Error: {str(e)}")
    
    return redirect(url_for('routes.settings'))

@routes.route("/list_items", methods=['GET'])
@login_required
def list_items():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    agents = Agent.query.filter_by(user_id=current_user.id).all()
    providers = Provider.query.filter_by(user_id=current_user.id).all()

    return jsonify({
        'projects': [{'id': p.id, 'title': p.title} for p in projects],
        'agents': [{'id': a.id, 'name': a.name, 'role': a.role} for a in agents],
        'providers': [{'id': p.id, 'provider_type': p.provider_type, 'model': p.model} for p in providers]
    })

