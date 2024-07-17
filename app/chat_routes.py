from flask import Blueprint, request, jsonify, flash
from flask_login import login_required, current_user
from .models import Agent, Provider, Project, db
from .utils import handle_error, log_info, log_debug, get_avatar_url
from .prompt_config import DEFAULT_PROMPTS
from .ollama_connection import connect_to_ollama

chat_routes = Blueprint('chat_routes', __name__)

@chat_routes.route("/chat", methods=["POST"])
@login_required
def chat():
    try:
        message = request.json.get('message')
        project_id = request.json.get('project_id')
        log_info(f"Received message: {message}")
        
        planner_agent = Agent.query.filter_by(user_id=current_user.id, role="AI Agent Project Planner").first()
        
        if not planner_agent:
            return handle_error(f"Missing AI agent for user {current_user.id}", 404)
        
        planner_provider = Provider.query.get(planner_agent.provider_id)
        
        if not planner_provider:
            return handle_error(f"Missing provider for agent {planner_agent.id}", 404)
        
        system_prompt = DEFAULT_PROMPTS.get(planner_agent.role, "")
        planner_prompt = f"{system_prompt}\n\nHuman: {message}\n\nAI:"
        log_debug(f"Prepared prompt: {planner_prompt[:100]}...")
        
        planner_response = get_ai_response(planner_provider, planner_prompt)
        
        if planner_response:
            log_info(f"Received AI response: {planner_response[:100]}...")
            journal_entry = f"User: {message}\n\nPlanner: {planner_response[:100]}..."
            
            project = Project.query.get(project_id)
            if project:
                project.journal = (project.journal or "") + "\n\n" + journal_entry
                db.session.commit()
            else:
                return handle_error(f"Project not found: {project_id}", 404)
            
            return jsonify({
                "planner_response": planner_response,
                "journal_entry": journal_entry,
                "planner_name": planner_agent.name,
                "planner_role": planner_agent.role,
                "planner_avatar": get_avatar_url(planner_agent.avatar)
            })
        else:
            return handle_error("Failed to get response from AI provider", 500)
    except Exception as e:
        return handle_error(f"An error occurred: {str(e)}", 500)

@chat_routes.route("/clear_journal", methods=["POST"])
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
        print(f"Connecting to Ollama at {provider.url}")
        print(f"Using model: {provider.model}")
        response_data = connect_to_ollama(provider.url, provider.model, prompt)
        
        print(f"Response data: {response_data}")
        
        if response_data:
            ai_response = response_data.get('response', '')
            if not ai_response and response_data.get('done_reason') == 'load':
                print("AI model is still loading")
                return "The AI model is still loading. Please try again in a moment."
            print(f"Received AI response: {ai_response[:100]}...")
            return ai_response
        else:
            print("Failed to get response from AI provider")
            return None
    else:
        print(f"Unsupported AI provider: {provider.provider_type}")
        return None
