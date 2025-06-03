from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Campaign, Option, Vote, User
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, BooleanField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, Length

admin = Blueprint('admin', __name__, url_prefix='/admin')

# Form for campaign options
class OptionForm(FlaskForm):
    text = StringField('Option Text', validators=[DataRequired(), Length(max=100)])

# Form for creating/editing campaigns
class CampaignForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    start_date = DateTimeField('Start Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_date = DateTimeField('End Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    is_active = BooleanField('Active')
    options = FieldList(FormField(OptionForm), min_entries=2)
    submit = SubmitField('Submit')

@admin.before_request
def check_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('main.index'))

@admin.route('/')
@login_required
def dashboard():
    campaigns_count = Campaign.query.count()
    active_campaigns = Campaign.query.filter(
        Campaign.is_active == True,
        Campaign.end_date > datetime.utcnow()
    ).count()
    users_count = User.query.count()
    votes_count = Vote.query.count()
    
    recent_campaigns = Campaign.query.order_by(Campaign.start_date.desc()).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        title='Admin Dashboard',
        campaigns_count=campaigns_count,
        active_campaigns=active_campaigns,
        users_count=users_count,
        votes_count=votes_count,
        recent_campaigns=recent_campaigns
    )

@admin.route('/campaigns')
@login_required
def manage_campaigns():
    campaigns = Campaign.query.order_by(Campaign.start_date.desc()).all()
    return render_template('admin/manage_campaigns.html', title='Manage Campaigns', campaigns=campaigns)

@admin.route('/campaign/new', methods=['GET', 'POST'])
@login_required
def create_campaign():
    form = CampaignForm()
    
    if form.validate_on_submit():
        campaign = Campaign(
            title=form.title.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_active=form.is_active.data
        )
        
        db.session.add(campaign)
        db.session.flush()  # Get the ID of the campaign before committing
        
        for option_form in form.options.data:
            option = Option(text=option_form['text'], campaign_id=campaign.id)
            db.session.add(option)
        
        db.session.commit()
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('admin.manage_campaigns'))
    
    return render_template('admin/create_campaign.html', title='Create Campaign', form=form)

@admin.route('/campaign/<int:campaign_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    form = CampaignForm()
    
    if form.validate_on_submit():
        campaign.title = form.title.data
        campaign.description = form.description.data
        campaign.start_date = form.start_date.data
        campaign.end_date = form.end_date.data
        campaign.is_active = form.is_active.data
        
        # Delete existing options and create new ones
        Option.query.filter_by(campaign_id=campaign.id).delete()
        
        for option_form in form.options.data:
            option = Option(text=option_form['text'], campaign_id=campaign.id)
            db.session.add(option)
        
        db.session.commit()
        flash('Campaign updated successfully!', 'success')
        return redirect(url_for('admin.manage_campaigns'))
    
    elif request.method == 'GET':
        form.title.data = campaign.title
        form.description.data = campaign.description
        form.start_date.data = campaign.start_date
        form.end_date.data = campaign.end_date
        form.is_active.data = campaign.is_active
        
        # Clear the existing options and repopulate
        form.options.pop_entry()
        form.options.pop_entry()
        
        for option in campaign.options:
            option_form = OptionForm()
            option_form.text = option.text
            form.options.append_entry(option_form.data)
    
    return render_template('admin/edit_campaign.html', title='Edit Campaign', form=form, campaign=campaign)

@admin.route('/campaign/<int:campaign_id>/delete', methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully!', 'success')
    return redirect(url_for('admin.manage_campaigns'))

@admin.route('/users')
@login_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', title='Manage Users', users=users)

@admin.route('/user/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    if user == current_user:
        flash('You cannot change your own admin status.', 'danger')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'Admin status for {user.username} has been {"granted" if user.is_admin else "revoked"}.', 'success')
    
    return redirect(url_for('admin.manage_users'))