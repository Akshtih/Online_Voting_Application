from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app import db, socketio
from app.models import Campaign, Option, Vote
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    active_campaigns = Campaign.query.filter(
        Campaign.is_active == True,
        Campaign.end_date > datetime.utcnow()
    ).all()
    return render_template('index.html', campaigns=active_campaigns)

@main.route('/campaigns')
def campaigns():
    active_campaigns = Campaign.query.filter(
        Campaign.is_active == True,
        Campaign.end_date > datetime.utcnow()
    ).all()
    past_campaigns = Campaign.query.filter(
        (Campaign.is_active == False) | (Campaign.end_date <= datetime.utcnow())
    ).all()
    return render_template('voting/campaigns.html', active_campaigns=active_campaigns, past_campaigns=past_campaigns)

@main.route('/campaign/<int:campaign_id>')
def campaign_detail(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    has_voted = False
    
    if current_user.is_authenticated:
        vote = Vote.query.filter_by(user_id=current_user.id, campaign_id=campaign_id).first()
        if vote:
            has_voted = True
            
    return render_template('voting/vote.html', campaign=campaign, has_voted=has_voted)

@main.route('/vote/<int:campaign_id>', methods=['POST'])
@login_required
def vote(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Check if campaign is active and not expired
    if not campaign.is_active or campaign.end_date <= datetime.utcnow():
        flash('This campaign is no longer active.', 'danger')
        return redirect(url_for('main.campaigns'))
    
    # Check if user has already voted in this campaign
    existing_vote = Vote.query.filter_by(user_id=current_user.id, campaign_id=campaign_id).first()
    if existing_vote:
        flash('You have already voted in this campaign.', 'warning')
        return redirect(url_for('main.results', campaign_id=campaign_id))
    
    option_id = request.form.get('option')
    if not option_id:
        flash('Please select an option to vote.', 'warning')
        return redirect(url_for('main.campaign_detail', campaign_id=campaign_id))
    
    option = Option.query.get_or_404(int(option_id))
    if option.campaign_id != campaign_id:
        flash('Invalid option selected.', 'danger')
        return redirect(url_for('main.campaign_detail', campaign_id=campaign_id))
    
    # Create and save the vote
    new_vote = Vote(user_id=current_user.id, campaign_id=campaign_id, option_id=option.id)
    db.session.add(new_vote)
    db.session.commit()
    
    # Emit socket event for real-time updates
    results_data = {
        'campaign_id': campaign_id,
        'options': [{'id': opt.id, 'text': opt.text, 'count': opt.get_vote_count()} for opt in campaign.options]
    }
    socketio.emit('vote_update', results_data)
    
    flash('Your vote has been recorded!', 'success')
    return redirect(url_for('main.results', campaign_id=campaign_id))

@main.route('/results/<int:campaign_id>')
def results(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template('results/results.html', campaign=campaign)