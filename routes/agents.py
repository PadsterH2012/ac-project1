from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models.models import db, Agent, Provider
from utils import save_avatar, get_avatar_url
from . import routes

@routes.route("/agent_settings", methods=["GET", "POST"])
@login_required
def agent_settings():
    providers = Provider.query.filter_by(user_id=current_user.id).all()
    if request.method == "POST":
        name = request.form.get('name')
        role = request.form.get('role')
        provider_id = request.form.get('provider_id')
        temperature = request.form.get('temperature')
        system_prompt = request.form.get('system_prompt')

        new_agent = Agent(
            name=name,
            role=role,
            provider_id=provider_id,
            temperature=temperature,
            system_prompt=system_prompt,
            user_id=current_user.id
        )

        if 'avatar' in request.files:
            avatar_file = request.files['avatar']
            avatar_filename = save_avatar(avatar_file)
            if avatar_filename:
                new_agent.avatar = avatar_filename

        db.session.add(new_agent)
        db.session.commit()

        flash('Agent added successfully!', 'success')
        return redirect(url_for('routes.agent_settings'))

    agents = Agent.query.filter_by(user_id=current_user.id).all()
    return render_template("agent_settings.html", providers=providers, agents=agents)

@routes.route("/edit_agent/<int:agent_id>", methods=["GET", "POST"])
@login_required
def edit_agent(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    if agent.user_id != current_user.id:
        flash('You do not have permission to edit this agent.', 'error')
        return redirect(url_for('routes.agent_settings'))
    
    providers = Provider.query.filter_by(user_id=current_user.id).all()
    
    if request.method == "POST":
        agent.name = request.form.get('name')
        agent.role = request.form.get('role')
        agent.provider_id = request.form.get('provider_id')
        agent.temperature = float(request.form.get('temperature'))
        agent.system_prompt = request.form.get('system_prompt')
        db.session.commit()
        flash('Agent updated successfully!', 'success')
        return redirect(url_for('routes.agent_settings'))
    
    return render_template("edit_agent.html", title="Edit Agent", agent=agent, providers=providers)

@routes.route("/delete_agent_from_settings/<int:agent_id>", methods=["POST"])
@login_required
def delete_agent_from_settings(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    if agent.user_id != current_user.id:
        flash('You do not have permission to delete this agent.', 'error')
        return redirect(url_for('routes.agent_settings'))
    
    db.session.delete(agent)
    db.session.commit()
    flash('Agent deleted successfully!', 'success')
    return redirect(url_for('routes.agent_settings'))
