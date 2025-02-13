from flask import request, jsonify
from flask_login import login_required, current_user
from models.models import db, Agent, Provider, Project, User
from services.prompt_config.prompt_config import DEFAULT_PROMPTS
from utils import get_avatar_url
from . import routes
from services.provider_connections.ollama_connection import connect_to_ollama

@routes.route("/create_hld", methods=["POST"])
@login_required
def create_hld():
    return create_design("hld", "AI Agent Architect")

@routes.route("/create_lld-db", methods=["POST"])
@login_required
def create_lld_db():
    return create_design("lld_db", "AI Agent DB SME")

@routes.route("/create_lld-ux", methods=["POST"])
@login_required
def create_lld_ux():
    return create_design("lld_ux", "AI Agent UX SME")

@routes.route("/create_lld-code", methods=["POST"])
@login_required
def create_lld_code():
    return create_design("lld_code", "AI Agent Coding SME")

@routes.route("/create_coding_plan", methods=["POST"])
@login_required
def create_coding_plan():
    try:
        project_id = request.json.get('project_id')
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"success": False, "error": f"Project not found: {project_id}"}), 404
        
        coding_sme_agent = Agent.query.filter_by(user_id=current_user.id, role="AI Agent Coding SME").first()
        if not coding_sme_agent:
            return jsonify({"success": False, "error": "AI Agent Coding SME not found"}), 404
        
        provider = Provider.query.get(coding_sme_agent.provider_id)
        if not provider:
            return jsonify({"success": False, "error": "Provider for AI Agent Coding SME not found"}), 404
        
        prompt = f"{DEFAULT_PROMPTS.get(coding_sme_agent.role, '')}\n\n"
        prompt += f"Current project scope:\n{project.scope or 'No scope defined yet.'}\n\n"
        prompt += f"High-Level Design:\n{project.hld or 'No HLD defined yet.'}\n\n"
        prompt += f"LLD-DB:\n{project.lld_db or 'No LLD-DB defined yet.'}\n\n"
        prompt += f"LLD-UX:\n{project.lld_ux or 'No LLD-UX defined yet.'}\n\n"
        prompt += f"LLD-Code:\n{project.lld_code or 'No LLD-Code defined yet.'}\n\n"
        prompt += "Based on this information, please create a comprehensive coding plan with milestones and phases. If you need clarification, you can communicate with other SMEs and the Architect.\n\nAI:"
        
        response = get_ai_response(provider, prompt)
        
        if response:
            project.coding_plan = response
            db.session.commit()
            
            return jsonify({
                "success": True, 
                "message": "Coding plan created successfully",
                "coding_plan": response
            })
        else:
            return jsonify({
                "success": False, 
                "error": "Failed to generate coding plan",
                "coding_plan": "No coding plan available yet."
            }), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def create_design(design_type, agent_role):
    try:
        project_id = request.json.get('project_id')
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"success": False, "error": f"Project not found: {project_id}"}), 404
        
        agent = Agent.query.filter_by(user_id=current_user.id, role=agent_role).first()
        if not agent:
            return jsonify({"success": False, "error": f"{agent_role} not found"}), 404
        
        provider = Provider.query.get(agent.provider_id)
        if not provider:
            return jsonify({"success": False, "error": f"Provider for {agent_role} not found"}), 404
        
        prompt = f"{DEFAULT_PROMPTS.get(agent.role, '')}\n\nCurrent project scope:\n{project.scope or 'No scope defined yet.'}\n\n"
        if design_type != "hld":
            prompt += f"High-Level Design:\n{project.hld or 'No HLD defined yet.'}\n\n"
        prompt += f"Based on this information, please create a {design_type.upper()} for the project.\n\nAI:"
        
        response = get_ai_response(provider, prompt)
        
        if response:
            # Store the design in the project
            setattr(project, design_type, response)
            db.session.commit()
            
            return jsonify({
                "success": True, 
                "message": f"{design_type.upper()} created successfully",
                design_type: response
            })
        else:
            return jsonify({"success": False, "error": f"Failed to generate {design_type.upper()}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

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
        architect_agent = Agent.query.filter_by(user_id=current_user.id, role="AI Agent Architect").first()
        db_sme_agent = Agent.query.filter_by(user_id=current_user.id, role="AI Agent DB SME").first()
        ux_sme_agent = Agent.query.filter_by(user_id=current_user.id, role="AI Agent UX SME").first()
        coding_sme_agent = Agent.query.filter_by(user_id=current_user.id, role="AI Agent Coding SME").first()
        
        if not writer_agent:
            writer_agent = create_default_agent(current_user.id, "AI Agent Project Writer")
        if not planner_agent:
            planner_agent = create_default_agent(current_user.id, "AI Agent Project Planner")
        if not architect_agent:
            architect_agent = create_default_agent(current_user.id, "AI Agent Architect")
        if not db_sme_agent:
            db_sme_agent = create_default_agent(current_user.id, "AI Agent DB SME")
        if not ux_sme_agent:
            ux_sme_agent = create_default_agent(current_user.id, "AI Agent UX SME")
        if not coding_sme_agent:
            coding_sme_agent = create_default_agent(current_user.id, "AI Agent Coding SME")
        
        if not all([writer_agent, planner_agent, architect_agent, db_sme_agent, ux_sme_agent, coding_sme_agent]):
            print(f"Failed to create default AI agents for user {current_user.id}")  # Log error
            return jsonify({"error": "Failed to create default AI agents for the current user"}), 500
        
        # Get the providers for the agents
        writer_provider = Provider.query.get(writer_agent.provider_id)
        planner_provider = Provider.query.get(planner_agent.provider_id)
        architect_provider = Provider.query.get(architect_agent.provider_id)
        db_sme_provider = Provider.query.get(db_sme_agent.provider_id)
        ux_sme_provider = Provider.query.get(ux_sme_agent.provider_id)
        coding_sme_provider = Provider.query.get(coding_sme_agent.provider_id)
        
        if not all([writer_provider, planner_provider, architect_provider, db_sme_provider, ux_sme_provider, coding_sme_provider]):
            print(f"Missing provider for agents")  # Log error
            return jsonify({"error": "Missing provider for the AI agents"}), 404
        
        # Generate or update project scope with the writer
        writer_prompt = f"{DEFAULT_PROMPTS.get(writer_agent.role, '')}\n\nCurrent project journal:\n{project.journal or 'No journal entries yet.'}\n\nBased on this information, please generate or update the project scope. If there are any unanswered items in the scope, list them at the end.\n\nAI:"
        scope_response = get_ai_response(writer_provider, writer_prompt)
        
        if scope_response:
            project.scope = scope_response
            db.session.commit()
        
        # Check if there are unanswered items in the scope
        unanswered_items = []
        if "Unanswered items:" in scope_response:
            unanswered_items = scope_response.split("Unanswered items:")[-1].strip().split("\n")
        
        # Prepare the planner prompt with the updated scope and journal
        system_prompt = DEFAULT_PROMPTS.get(planner_agent.role, "")
        planner_prompt = f"{system_prompt}\n\nCurrent project scope:\n{project.scope or 'No scope defined yet.'}\n\nProject journal:\n{project.journal or 'No journal entries yet.'}\n\n"

        if unanswered_items:
            planner_prompt += f"There are some unanswered items in the project scope. Please ask the user about these items one by one, but only if they haven't been addressed in the journal:\n\n" + "\n".join(unanswered_items) + "\n\n"

        planner_prompt += f"Human: {message}\n\nAI:"
        
        print(f"Prepared prompt: {planner_prompt[:100]}...")  # Log prepared prompt (truncated)
        
        # Make request to the AI provider for the planner
        planner_response = get_ai_response(planner_provider, planner_prompt)
        
        if planner_response:
            print(f"Received AI response: {planner_response[:100]}...")  # Log AI response (truncated)
            # Create a journal entry in markdown format
            journal_entry = f"## User\n\n{message}\n\n## Planner\n\n{planner_response}"
            
            # Update the project journal
            project.journal = (project.journal or "") + "\n\n---\n\n" + journal_entry
            db.session.commit()
            
            # Update the scope after the planner's response
            writer_prompt = f"{DEFAULT_PROMPTS.get(writer_agent.role, '')}\n\nCurrent project journal:\n{project.journal}\n\nBased on this information, please generate or update the project scope.\n\nAI:"
            updated_scope_response = get_ai_response(writer_provider, writer_prompt)
            
            if updated_scope_response:
                structured_scope = structure_project_scope(updated_scope_response)
                project.scope = structured_scope
                db.session.commit()
            
            return jsonify({
                "planner_response": planner_response,
                "journal_entry": journal_entry,
                "planner_name": planner_agent.name,
                "planner_role": planner_agent.role,
                "planner_avatar": get_avatar_url(planner_agent.avatar),
                "project_scope": project.scope
            })
        else:
            print("Failed to get response from AI provider")  # Log error
            return jsonify({"error": "Failed to get response from AI provider"}), 500
    except Exception as e:
        print(f"An error occurred: {str(e)}")  # Log the specific error
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def structure_project_scope(scope_text):
    structured_scope = ""
    current_section = ""
    unanswered_items = []

    lines = scope_text.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if line == "":
            continue
        if line.lower() == "unanswered items:":
            break
        if line.endswith(':'):
            current_section = line.rstrip(':')
            structured_scope += f"## {current_section}\n\n"
        elif line.startswith('*') or line.startswith('-'):
            structured_scope += f"{line}\n"
        elif line[0].isdigit() and line[1] == '.':
            # This is a numbered item, treat it as a subsection
            subsection = line[2:].strip()
            structured_scope += f"### {subsection}\n\n"
        else:
            # Check if the next line is a list item
            if i + 1 < len(lines) and (lines[i+1].strip().startswith('*') or lines[i+1].strip().startswith('-')):
                structured_scope += f"### {line}\n\n"
            else:
                structured_scope += f"{line}\n\n"

    if "Unanswered items:" in scope_text:
        unanswered = scope_text.split("Unanswered items:")[-1].strip().split('\n')
        structured_scope += "## Unanswered items\n\n"
        for item in unanswered:
            structured_scope += f"- {item.strip()}\n"

    return structured_scope.strip()

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
