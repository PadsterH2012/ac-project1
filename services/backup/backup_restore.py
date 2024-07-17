import json
from models import User, Project, Agent, Provider, db

def backup_data(user_id, backup_type='all'):
    user = User.query.get(user_id)
    if not user:
        return json.dumps({"error": "User not found"})

    backup_data = {"user": user.to_dict()}

    if backup_type == 'all' or 'projects' in backup_type:
        backup_data["projects"] = [project.to_dict() for project in user.projects]

    if backup_type == 'all' or 'agents' in backup_type:
        backup_data["agents"] = [agent.to_dict() for agent in user.agents]

    if backup_type == 'all' or 'providers' in backup_type:
        backup_data["providers"] = [provider.to_dict() for provider in user.providers]

    return json.dumps(backup_data)

def restore_data(user_id, backup_data_json):
    backup_data = json.loads(backup_data_json)
    user = User.query.get(user_id)

    if not user:
        raise ValueError("User not found")

    if "projects" in backup_data:
        for project_data in backup_data["projects"]:
            project = Project.from_dict(project_data)
            project.user_id = user.id
            db.session.add(project)

    if "agents" in backup_data:
        for agent_data in backup_data["agents"]:
            agent = Agent.from_dict(agent_data)
            agent.user_id = user.id
            db.session.add(agent)

    if "providers" in backup_data:
        for provider_data in backup_data["providers"]:
            provider = Provider(**provider_data)
            provider.user_id = user.id
            db.session.add(provider)

    db.session.commit()
