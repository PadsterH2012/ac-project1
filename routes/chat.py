from flask import request, jsonify
from flask_login import login_required, current_user
from models.models import db, Agent, Provider, Project, User
from services.prompt_config.prompt_config import DEFAULT_PROMPTS
from utils import get_avatar_url
from . import routes
from services.provider_connections.ollama_connection import connect_to_ollama

@routes.route("/chat", methods=["POST"])
@login_required
def chat():
    try:
        message = request.json.get('message')
        project_id = request.json.get('project_id')
        print(f"Received message: {message}")  # Log received message
        
        project = Project.query.get(project_id)
        if not project:
            print(f"Project not found: {project_id}")  # Log if project is not found
            return jsonify({"error": f"Project not found: {project_id}"}), 404
        
        # Get or create the current user's AI agents
        writer_agent = Agent.query.filter_by(user_id=current_user.id, role="AI Agent Project Writer").first()
        planner_agent = Agent.query.filter_by(user_id=current_user.id, role="AI Agent Project Planner").first()
        
        if not writer_agent:
            writer_agent = create_default_agent(current_user.id, "AI Agent Project Writer")
        if not planner_agent:
            planner_agent = create_default_agent(current_user.id, "AI Agent Project Planner")
        
        if not writer_agent or not planner_agent:
            print(f"Failed to create default AI agents for user {current_user.id}")  # Log error
            return jsonify({"error": "Failed to create default AI agents for the current user"}), 500
        
        # Get the providers for the agents
        writer_provider = Provider.query.get(writer_agent.provider_id)
        planner_provider = Provider.query.get(planner_agent.provider_id)
        
        if not writer_provider or not planner_provider:
            print(f"Missing provider for agents")  # Log error
            return jsonify({"error": "Missing provider for the AI agents"}), 404
        
        # Generate or update project scope with the writer
        writer_prompt = f"{DEFAULT_PROMPTS.get(writer_agent.role, '')}\n\nCurrent project journal:\n{project.journal or 'No journal entries yet.'}\n\nBased on this information, please generate or update the project scope.\n\nAI:"
        scope_response = get_ai_response(writer_provider, writer_prompt)
        
        if scope_response:
            project.scope = scope_response
            db.session.commit()
        
        # Prepare the planner prompt with the updated scope
        system_prompt = DEFAULT_PROMPTS.get(planner_agent.role, "")
        planner_prompt = f"{system_prompt}\n\nCurrent project scope:\n{project.scope or 'No scope defined yet.'}\n\nHuman: {message}\n\nAI:"
        print(f"Prepared prompt: {planner_prompt[:100]}...")  # Log prepared prompt (truncated)
        
        # Make request to the AI provider for the planner
        planner_response = get_ai_response(planner_provider, planner_prompt)
        
        if planner_response:
            print(f"Received AI response: {planner_response[:100]}...")  # Log AI response (truncated)
            # Create a journal entry
            journal_entry = f"User: {message}\n\nPlanner: {planner_response}"
            
            # Update the project journal
            project.journal = (project.journal or "") + "\n\n" + journal_entry
            db.session.commit()
            
            return jsonify({
                "planner_response": planner_response,
                "journal_entry": journal_entry,
                "planner_name": planner_agent.name,
                "planner_role": planner_agent.role,
                "planner_avatar": get_avatar_url(planner_agent.avatar)
            })
        else:
            print("Failed to get response from AI provider")  # Log error
            return jsonify({"error": "Failed to get response from AI provider"}), 500
    except Exception as e:
        print(f"An error occurred: {str(e)}")  # Log the specific error
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@routes.route("/clear_journal", methods=["POST"])
@login_required
def clear_journal():
    project_id = request.json.get('project_id')
    project = Project.query.get(project_id)
    if project and project.user_id == current_user.id:
        project.journal = ""
        db.session.commit()
        return jsonify({"success": True, "message": "Journal cleared successfully"})
    return jsonify({"success": False, "message": "Failed to clear journal"}), 404

def get_ai_response(provider, prompt):
    if provider.provider_type == 'ollama':
        print(f"Connecting to Ollama at {provider.url}")  # Log connection attempt
        print(f"Using model: {provider.model}")  # Log model being used
        response_data = connect_to_ollama(provider.url, provider.model, prompt)
        
        print(f"Response data: {response_data}")  # Log full response data
        
        if response_data:
            ai_response = response_data.get('response', '')
            if not ai_response and response_data.get('done_reason') == 'load':
                print("AI model is still loading")  # Log loading status
                return "The AI model is still loading. Please try again in a moment."
            print(f"Received AI response: {ai_response[:100]}...")  # Log (truncated) AI response
            return ai_response
        else:
            print("Failed to get response from AI provider")  # Log error
            return None
    else:
        print(f"Unsupported AI provider: {provider.provider_type}")  # Log error
        return None

def create_default_agent(user_id, role):
    default_provider = Provider.query.filter_by(user_id=user_id).first()
    if not default_provider:
        default_provider = Provider(
            user_id=user_id,
            provider_type='ollama',
            api_key='',
            model='llama2',
            url='http://localhost:11434/api/generate'
        )
        db.session.add(default_provider)
        db.session.commit()

    new_agent = Agent(
        name=role,
        role=role,
        user_id=user_id,
        provider_id=default_provider.id,
        temperature=0.7,
        system_prompt=DEFAULT_PROMPTS.get(role, "")
    )
    db.session.add(new_agent)
    db.session.commit()
    return new_agent
