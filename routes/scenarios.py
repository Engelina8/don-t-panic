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
    stage_index = data.get('stage_index')
    option_index = data.get('option_index')
    
    if stage_index is None or option_index is None:
        return jsonify({'error': 'Invalid decision data'}), 400
    
    # Parse scenario content
    import json
    try:
        scenario_data = json.loads(session.scenario.scenario_content)
    except:
        return jsonify({'error': 'Failed to parse scenario'}), 500
    
    # Get the selected option
    if stage_index >= len(scenario_data.get('stages', [])):
        return jsonify({'error': 'Invalid stage'}), 400
    
    stage = scenario_data['stages'][stage_index]
    if option_index >= len(stage.get('options', [])):
        return jsonify({'error': 'Invalid option'}), 400
    
    selected_option = stage['options'][option_index]
    
    # Initialize or get session_data
    session_data_dict = {}
    if session.session_data:
        try:
            session_data_dict = json.loads(session.session_data)
        except:
            session_data_dict = {}
    
    # Initialize path tracking if not present
    if 'path' not in session_data_dict:
        session_data_dict['path'] = []
        session_data_dict['path_points'] = 0
        session_data_dict['path_max_points'] = 0
        session_data_dict['path_metrics'] = {
            'detection': 0,
            'containment': 0,
            'eradication': 0,
            'recovery': 0,
            'communication': 0
        }
        session_data_dict['available_metrics'] = {
            'detection': 0,
            'containment': 0,
            'eradication': 0,
            'recovery': 0,
            'communication': 0
        }
    
    # Record the decision
    session_data_dict['path'].append({
        'stage_index': stage_index,
        'stage_name': stage.get('stage', 'Unknown'),
        'option_index': option_index,
        'option_text': selected_option.get('text', ''),
        'points': selected_option.get('points', 0)
    })
    
    # Add points to path total
    session_data_dict['path_points'] += selected_option.get('points', 0)
    
    # Calculate max points available at this stage
    max_points_in_stage = max([opt.get('points', 0) for opt in stage.get('options', [])], default=0)
    session_data_dict['path_max_points'] += max_points_in_stage
    
    # Update path metrics with earned points from this option
    for metric in ['detection', 'containment', 'eradication', 'recovery', 'communication']:
        earned = selected_option.get(metric, 0)
        session_data_dict['path_metrics'][metric] += earned
    
    # Update available metrics from the question's metrics list
    for metric in stage.get('metrics', []):
        # Find max available for this metric in this stage
        max_metric_in_stage = 0
        for option in stage.get('options', []):
            metric_value = option.get(metric, 0)
            if metric_value > max_metric_in_stage:
                max_metric_in_stage = metric_value
        session_data_dict['available_metrics'][metric] += max_metric_in_stage
    
    # Save updated session data
    session.session_data = json.dumps(session_data_dict)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error saving session data: {e}")
        return jsonify({'error': 'Failed to save decision'}), 500
    
    return jsonify({
        'success': True,
        'message': 'Decision recorded',
        'current_score': session_data_dict['path_points'],
        'stage_complete': True
    })

@scenario_bp.route('/session/<int:session_id>/complete', methods=['POST'])
@login_required
def complete(session_id):
    """Complete a training session"""
    session = TrainingSession.query.get_or_404(session_id)
    
    # Security check
    if session.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get session data with path information
    import json
    session_data_dict = {}
    if session.session_data:
        try:
            session_data_dict = json.loads(session.session_data)
        except Exception as e:
            print(f"Error parsing session_data: {e}")
            session_data_dict = {}
    
    # Get final score based on path taken
    final_score = session_data_dict.get('path_points', 0)
    path_metrics = session_data_dict.get('path_metrics', {
        'detection': 0,
        'containment': 0,
        'eradication': 0,
        'recovery': 0,
        'communication': 0
    })
    available_metrics = session_data_dict.get('available_metrics', {
        'detection': 0,
        'containment': 0,
        'eradication': 0,
        'recovery': 0,
        'communication': 0
    })
    
    # Calculate outcome based on percentage of path maximum (not scenario maximum)
    # path_max_points was calculated in submit_decision as we went through the path
    path_total_available = session_data_dict.get('path_max_points', 0)
    
    if path_total_available > 0:
        percentage = (final_score / path_total_available) * 100
    else:
        percentage = 0
    
    # Ensure percentage doesn't exceed 100
    percentage = min(100, percentage)
    
    # Update session fields
    session.status = 'completed'
    session.completed_at = datetime.utcnow()
    session.score = int(percentage) if isinstance(percentage, (int, float)) else 0
    
    # Save breakdown metrics based on path taken
    session.detection_score = int(path_metrics.get('detection', 0))
    session.containment_score = int(path_metrics.get('containment', 0))
    session.eradication_score = int(path_metrics.get('eradication', 0))
    session.recovery_score = int(path_metrics.get('recovery', 0))
    session.communication_score = int(path_metrics.get('communication', 0))
    
    # Store important info in session_data
    session_data_dict['path_max_points'] = session.scenario.max_points
    session_data_dict['metrics_max'] = available_metrics
    session_data_dict['path_metrics_earned'] = path_metrics
    session_data_dict['path_total_available'] = path_total_available
    session.session_data = json.dumps(session_data_dict)
    
    if percentage >= 80:
        session.outcome = 'success'
    elif percentage >= 60:
        session.outcome = 'partial_success'
    elif percentage >= 40:
        session.outcome = 'neutral'
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
        return jsonify({'error': f'Failed to complete session: {str(e)}'}), 500

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
    
    # Extract metrics from session_data
    path_metrics_earned = {}
    metrics_max = {}
    path_total_available = 0
    path_points_earned = 0
    
    if session.session_data:
        import json
        try:
            session_data_dict = json.loads(session.session_data)
            path_metrics_earned = session_data_dict.get('path_metrics_earned', {})
            metrics_max = session_data_dict.get('metrics_max', {})
            # Use the score and path_total_available from complete() which was already calculated
            path_points_earned = session_data_dict.get('path_points', 0)
            path_total_available = session_data_dict.get('path_total_available', 0)
        except:
            pass
    
    # Fallback values
    if not path_metrics_earned:
        path_metrics_earned = {
            'detection': session.detection_score or 0,
            'containment': session.containment_score or 0,
            'eradication': session.eradication_score or 0,
            'recovery': session.recovery_score or 0,
            'communication': session.communication_score or 0
        }
    
    if not metrics_max:
        metrics_max = {
            'detection': 0,
            'containment': 0,
            'eradication': 0,
            'recovery': 0,
            'communication': 0
        }
    
    if path_total_available == 0:
        path_total_available = session.scenario.max_points
    
    return render_template('scenarios/results.html',
                         session=session,
                         scenario=session.scenario,
                         path_metrics_earned=path_metrics_earned,
                         metrics_max=metrics_max,
                         path_total_available=path_total_available)
