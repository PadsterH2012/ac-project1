import json
from models import db, User, Project, Agent, Provider

def backup_data(user_id, backup_type='all'):
    data = {}
    
    user = User.query.get(user_id)
    if not user:
        return json.dumps({}, indent=2)
    
    data['user'] = user.to_dict()
    
    if backup_type in ['all', 'projects']:
        projects = Project.query.filter_by(user_id=user_id).all()
        if projects:
            data['projects'] = [project.to_dict() for project in projects]
    
    if backup_type in ['all', 'agents']:
        agents = Agent.query.filter_by(user_id=user_id).all()
        if agents:
            data['agents'] = [agent.to_dict() for agent in agents]
    
    if backup_type in ['all', 'providers']:
        providers = Provider.query.filter_by(user_id=user_id).all()
        if providers:
            data['providers'] = [provider.to_dict() for provider in providers]
    
    # Check if any data was collected beyond user data
    if len(data) == 1 and 'user' in data:
        print("No additional data found for the specified user and backup type")
        return json.dumps({}, indent=2)
    
    return json.dumps(data, indent=2)

def restore_data(user_id, backup_data):
    data = json.loads(backup_data)
    
    if 'projects' in data:
        for project_data in data['projects']:
            project = Project.from_dict(project_data)
            project.user_id = user_id
            db.session.add(project)
    
    if 'agents' in data:
        for agent_data in data['agents']:
            agent = Agent.from_dict(agent_data)
            agent.user_id = user_id
            db.session.add(agent)
    
    if 'providers' in data:
        for provider_data in data['providers']:
            provider = Provider.from_dict(provider_data)
            provider.user_id = user_id
            db.session.add(provider)
    
    db.session.commit()

def backup_to_file(user_id, filename, backup_type='all'):
    data = backup_data(user_id, backup_type)
    with open(filename, 'w') as f:
        f.write(data)

def restore_from_file(user_id, filename):
    with open(filename, 'r') as f:
        backup_data = f.read()
    restore_data(user_id, backup_data)
