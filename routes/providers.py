from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import Provider, db
from . import routes

@routes.route("/provider_settings")
@login_required
def provider_settings():
    providers = Provider.query.filter_by(user_id=current_user.id).all()
    return render_template("provider_settings.html", providers=providers)

@routes.route("/add_provider", methods=["POST"])
@login_required
def add_provider():
    provider_type = request.form.get('provider_type')
    api_key = request.form.get('api_key')
    model = request.form.get('model')
    url = request.form.get('url')

    new_provider = Provider(
        user_id=current_user.id,
        provider_type=provider_type,
        api_key=api_key,
        model=model,
        url=url if provider_type == 'ollama' else None
    )

    db.session.add(new_provider)
    db.session.commit()

    flash('Provider added successfully!', 'success')
    return redirect(url_for('routes.provider_settings'))

@routes.route("/edit_provider/<int:provider_id>", methods=["GET", "POST"])
@login_required
def edit_provider(provider_id):
    provider = Provider.query.get_or_404(provider_id)
    if provider.user_id != current_user.id:
        flash('You do not have permission to edit this provider.', 'error')
        return redirect(url_for('routes.provider_settings'))
    
    if request.method == "POST":
        provider.provider_type = request.form.get('provider_type')
        provider.api_key = request.form.get('api_key')
        provider.model = request.form.get('model')
        provider.url = request.form.get('url') if provider.provider_type == 'ollama' else None
        db.session.commit()
        flash('Provider updated successfully!', 'success')
        return redirect(url_for('routes.provider_settings'))
    
    return render_template("edit_provider.html", provider=provider)

@routes.route("/delete_provider/<int:provider_id>", methods=["POST"])
@login_required
def delete_provider(provider_id):
    provider = Provider.query.get_or_404(provider_id)
    if provider.user_id != current_user.id:
        flash('You do not have permission to delete this provider.', 'error')
        return redirect(url_for('routes.provider_settings'))
    db.session.delete(provider)
    db.session.commit()
    flash('Provider deleted successfully!', 'success')
    return redirect(url_for('routes.provider_settings'))
