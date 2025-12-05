"""Scenario routes - List, Start, Play scenarios"""

from flask import render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from models import db, Scenario, TrainingSession
from datetime import datetime
from . import scenario_bp

@scenario_bp.route('/')
@login_required
def list():
    """List all available scenarios"""
    scenarios = Scenario.query.all()
    
    # Get user's completed scenarios
    completed_sessions = TrainingSession.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).all()
    
    completed_scenario_ids = [session.scenario_id for session in completed_sessions]
    
    return render_template('scenarios/list.html', 
                         scenarios=scenarios,
                         completed_ids=completed_scenario_ids)

@scenario_bp.route('/<int:scenario_id>')
@login_required
def detail(scenario_id):
    """Show scenario details"""
    scenario = Scenario.query.get_or_404(scenario_id)
    
    # Get user's previous attempts
    previous_sessions = TrainingSession.query.filter_by(
        user_id=current_user.id,
        scenario_id=scenario_id
    ).order_by(TrainingSession.started_at.desc()).all()
    
    return render_template('scenarios/detail.html',
                         scenario=scenario,
                         previous_sessions=previous_sessions)

@scenario_bp.route('/<int:scenario_id>/start', methods=['POST'])
@login_required
def start(scenario_id):
    """Start a new training scenario"""
    scenario = Scenario.query.get_or_404(scenario_id)
    
    # Check if user has an active session for this scenario
    active_session = TrainingSession.query.filter_by(
        user_id=current_user.id,
        scenario_id=scenario_id,
        status='in_progress'
    ).first()
    
    if active_session:
        flash('You already have an active session for this scenario', 'warning')
        return redirect(url_for('scenarios.play', session_id=active_session.id))
    
    # Create new training session
    new_session = TrainingSession(
        user_id=current_user.id,
        scenario_id=scenario.id,
        status='in_progress',
        started_at=datetime.utcnow()
    )
    
    try:
        db.session.add(new_session)
        db.session.commit()
        flash(f'Started: {scenario.title}', 'success')
        return redirect(url_for('scenarios.play', session_id=new_session.id))
    except Exception as e:
        db.session.rollback()
        flash('Failed to start scenario', 'error')
        print(f"Error starting scenario: {e}")
        return redirect(url_for('scenarios.list'))

@scenario_bp.route('/session/<int:session_id>')
@login_required
def play(session_id):
    """Play a scenario"""
    session = TrainingSession.query.get_or_404(session_id)
    
    # Security: Make sure user owns this session
    if session.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('scenarios.list'))
    
    # If session is completed, show results
    if session.status == 'completed':
        return redirect(url_for('scenarios.results', session_id=session_id))
    
    return render_template('scenarios/play.html',
                         session=session,
                         scenario=session.scenario)

@scenario_bp.route('/session/<int:session_id>/submit', methods=['POST'])
@login_required
def submit_decision(session_id):
    """Submit a decision during gameplay"""
    session = TrainingSession.query.get_or_404(session_id)
    
    # Security check
    if session.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get decision data
    data = request.get_json()
    decision = data.get('decision')
    
    # TODO: Process decision, update game state
    # For now, just acknowledge
    
    return jsonify({
        'success': True,
        'message': 'Decision recorded'
    })

@scenario_bp.route('/session/<int:session_id>/complete', methods=['POST'])
@login_required
def complete(session_id):
    """Complete a training session"""
    session = TrainingSession.query.get_or_404(session_id)
    
    # Security check
    if session.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get final score and optional metrics breakdown
    data = request.get_json() or {}
    final_score = data.get('score', 0)
    metrics = data.get('metrics', {})

    # Update session fields
    session.status = 'completed'
    session.completed_at = datetime.utcnow()
    try:
        session.score = int(final_score)
    except Exception:
        session.score = 0

    # Save breakdown metrics if provided (default to 0)
    session.detection_score = int(metrics.get('detection', session.detection_score or 0))
    session.containment_score = int(metrics.get('containment', session.containment_score or 0))
    session.eradication_score = int(metrics.get('eradication', session.eradication_score or 0))
    session.recovery_score = int(metrics.get('recovery', session.recovery_score or 0))
    session.communication_score = int(metrics.get('communication', session.communication_score or 0))

    # Derive simple outcome label
    if session.score >= 80:
        session.outcome = 'success'
    elif session.score >= 60:
        session.outcome = 'partial_success'
    else:
        session.outcome = 'failure'

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'redirect': url_for('scenarios.results', session_id=session_id)
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error completing session: {e}")
        return jsonify({'error': 'Failed to complete session'}), 500

@scenario_bp.route('/session/<int:session_id>/results')
@login_required
def results(session_id):
    """Show scenario results"""
    session = TrainingSession.query.get_or_404(session_id)
    
    # Security check
    if session.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('scenarios.list'))
    
    if session.status != 'completed':
        flash('Session not yet completed', 'warning')
        return redirect(url_for('scenarios.play', session_id=session_id))
    
    return render_template('scenarios/results.html',
                         session=session,
                         scenario=session.scenario)
