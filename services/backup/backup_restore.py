import json
from models import db
from models.models import User, Project, Agent, Provider

def backup_data(user_id, backup_type='all'):
    user = User.query.get(user_id)
    if not user:
        return json.dumps({"error": "User not found"})

    backup_data = {
        "user": user.to_dict(),
        "projects": [],
        "agents": [],
        "providers": []
    }

    if backup_type == 'all' or 'projects' in backup_type:
        backup_data["projects"] = [
            {
                "id": project.id,
                "title": project.title,
                "description": project.description,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
                "journal": project.journal
            } for project in user.projects
        ]

    if backup_type == 'all' or 'agents' in backup_type:
        backup_data["agents"] = [
            {
                "id": agent.id,
                "name": agent.name,
                "role": agent.role,
                "provider_id": agent.provider_id,
                "temperature": agent.temperature,
                "system_prompt": agent.system_prompt,
                "avatar": agent.avatar
            } for agent in user.agents
        ]

    if backup_type == 'all' or 'providers' in backup_type:
        backup_data["providers"] = [
            {
                "id": provider.id,
                "provider_type": provider.provider_type,
                "api_key": provider.api_key,
                "model": provider.model,
                "url": provider.url
            } for provider in user.providers
        ]

    return json.dumps(backup_data, indent=2)

def restore_data(user_id, backup_data_json, selected_items):
    from datetime import datetime  # Explicitly import datetime here
    
    backup_data = json.loads(backup_data_json)
    user = User.query.get(user_id)

    if not user:
        raise ValueError("User not found")

    if "projects" in backup_data and "projects" in selected_items:
        for project_data in backup_data["projects"]:
            if f"project_{project_data['id']}" in selected_items:
                project = Project(
                    title=project_data['title'],
                    description=project_data['description'],
                    user_id=user.id,
                    journal=project_data['journal']
                )
                project.created_at = datetime.fromisoformat(project_data['created_at'])
                project.updated_at = datetime.fromisoformat(project_data['updated_at'])
                db.session.add(project)

    if "agents" in backup_data and "agents" in selected_items:
        for agent_data in backup_data["agents"]:
            if f"agent_{agent_data['id']}" in selected_items:
                agent = Agent(
                    name=agent_data['name'],
                    role=agent_data['role'],
                    user_id=user.id,
                    provider_id=None,  # We'll update this after restoring providers
                    temperature=agent_data['temperature'],
                    system_prompt=agent_data['system_prompt'],
                    avatar=agent_data['avatar']
                )
                db.session.add(agent)

    if "providers" in backup_data and "providers" in selected_items:
        for provider_data in backup_data["providers"]:
            if f"provider_{provider_data['id']}" in selected_items:
                provider = Provider(
                    user_id=user.id,
                    provider_type=provider_data['provider_type'],
                    api_key=provider_data['api_key'],
                    model=provider_data['model'],
                    url=provider_data['url']
                )
                db.session.add(provider)

    db.session.commit()

    # Update agent provider_id after restoring providers
    if "agents" in backup_data and "agents" in selected_items:
        for agent_data in backup_data["agents"]:
            if f"agent_{agent_data['id']}" in selected_items:
                agent = Agent.query.filter_by(user_id=user.id, name=agent_data['name']).first()
                if agent:
                    provider = Provider.query.filter_by(user_id=user.id, provider_type=agent_data['provider_type']).first()
                    if provider:
                        agent.provider_id = provider.id
                        db.session.add(agent)

    db.session.commit()
