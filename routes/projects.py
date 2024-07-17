from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db
from models.project import Project
from . import routes

@routes.route("/projects")
@login_required
def projects():
    user_projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template("projects.html", projects=user_projects)

@routes.route("/continue_project/<int:project_id>")
@login_required
def continue_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('You do not have permission to access this project.', 'error')
        return redirect(url_for('routes.projects'))
    return render_template("chat_interface.html", project=project, journal_entries=project.journal)

@routes.route("/create_project", methods=["GET", "POST"])
@login_required
def create_project():
    if request.method == "POST":
        title = request.form.get('title')
        description = request.form.get('description')
        new_project = Project(title=title, description=description, user_id=current_user.id)
        db.session.add(new_project)
        db.session.commit()
        flash('Project created successfully!', 'success')
        return redirect(url_for('routes.projects'))
    return render_template("create_project.html")

@routes.route("/delete_project/<int:project_id>", methods=["POST"])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('You do not have permission to delete this project.', 'error')
        return redirect(url_for('routes.projects'))
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('routes.projects'))

@routes.route("/edit_project/<int:project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('You do not have permission to edit this project.', 'error')
        return redirect(url_for('routes.projects'))
    
    if request.method == "POST":
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('routes.projects'))
    
    return render_template("edit_project.html", project=project)
