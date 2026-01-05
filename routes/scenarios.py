"""Scenario routes - List, Start, Play scenarios"""

from flask import render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from models import db, Scenario, TrainingSession
from scenario_manager import scenario_manager
from datetime import datetime
import json
from . import scenario_bp

@scenario_bp.route('/')
@login_required
def list():
    """List all available scenarios grouped by category"""
    scenarios_data = scenario_manager.get_all_scenarios()


    completed_sessions = TrainingSession.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).all()

    completed_scenario_ids = [session.scenario_id for session in completed_sessions]


    scenarios_by_category = {}
    uncategorized = []

    for data in scenarios_data:
        scenario = Scenario(data)
        category = scenario.category if scenario.category else None

        if category:
            if category not in scenarios_by_category:
                scenarios_by_category[category] = []
            scenarios_by_category[category].append(scenario)
        else:
            uncategorized.append(scenario)

    return render_template('scenarios/list.html',
                         scenarios_by_category=scenarios_by_category,
                         uncategorized_scenarios=uncategorized,
                         completed_ids=completed_scenario_ids)

@scenario_bp.route('/<scenario_id>')
@login_required
def detail(scenario_id):
    """Show scenario details"""
    scenario_data = scenario_manager.get_scenario(scenario_id)

    if not scenario_data:
        flash('Scenario not found', 'error')
        return redirect(url_for('scenarios.list'))

    scenario = Scenario(scenario_data)

    all_sessions = TrainingSession.query.filter_by(
        scenario_id=scenario_id,
        status='completed'
    ).all()

    scenario.times_played = len(all_sessions)
    if all_sessions:
        scores = [s.score for s in all_sessions if s.score]
        scenario.average_score = (sum(scores) / len(scores)) if scores else 0
    else:
        scenario.average_score = None

    previous_sessions = TrainingSession.query.filter_by(
        user_id=current_user.id,
        scenario_id=scenario_id
    ).order_by(TrainingSession.started_at.desc()).all()

    return render_template('scenarios/detail.html',
                         scenario=scenario,
                         previous_sessions=previous_sessions)

@scenario_bp.route('/<scenario_id>/start', methods=['POST'])
@login_required
def start(scenario_id):
    """Start a new training scenario"""
    scenario_data = scenario_manager.get_scenario(scenario_id)

    if not scenario_data:
        flash('Scenario not found', 'error')
        return redirect(url_for('scenarios.list'))

    scenario = Scenario(scenario_data)


    active_session = TrainingSession.query.filter_by(
        user_id=current_user.id,
        scenario_id=scenario_id,
        status='in_progress'
    ).first()

    if active_session:
        flash('You already have an active session for this scenario', 'warning')
        return redirect(url_for('scenarios.play', session_id=active_session.id))


    new_session = TrainingSession(
        user_id=current_user.id,
        scenario_id=scenario_id,
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

    if session.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('scenarios.list'))

    if session.status == 'completed':
        return redirect(url_for('scenarios.results', session_id=session_id))

    scenario_data = scenario_manager.get_scenario(session.scenario_id)
    scenario = Scenario(scenario_data) if scenario_data else None

    return render_template('scenarios/play.html',
                         session=session,
                         scenario=scenario)

@scenario_bp.route('/session/<int:session_id>/submit', methods=['POST'])
@login_required
def submit_decision(session_id):
    """Submit a decision during gameplay"""
    session = TrainingSession.query.get_or_404(session_id)


    if session.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403


    data = request.get_json()
    stage_index = data.get('stage_index')
    option_index = data.get('option_index')

    if stage_index is None or option_index is None:
        return jsonify({'error': 'Invalid decision data'}), 400


    try:
        scenario_data_dict = scenario_manager.get_scenario(str(session.scenario_id))
        if not scenario_data_dict:
            return jsonify({'error': 'Scenario not found'}), 404
    except Exception:
        return jsonify({'error': 'Failed to load scenario'}), 500


    scenario_content = scenario_data_dict.get('scenario_content', {})


    if stage_index >= len(scenario_content.get('stages', [])):
        return jsonify({'error': 'Invalid stage'}), 400

    stage = scenario_content['stages'][stage_index]
    if option_index >= len(stage.get('options', [])):
        return jsonify({'error': 'Invalid option'}), 400

    selected_option = stage['options'][option_index]


    session_data_dict = {}
    if session.session_data:
        try:
            session_data_dict = json.loads(session.session_data)
        except Exception:
            session_data_dict = {}


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


    session_data_dict['path'].append({
        'stage_index': stage_index,
        'stage_name': stage.get('stage', 'Unknown'),
        'option_index': option_index,
        'option_text': selected_option.get('text', ''),
        'points': selected_option.get('points', 0)
    })


    session_data_dict['path_points'] += selected_option.get('points', 0)

    print(f"DEBUG submit_decision(): stage {stage_index}, option {option_index}, points {selected_option.get('points', 0)}, total path_points now = {session_data_dict['path_points']}")


    max_points_in_stage = max([opt.get('points', 0) for opt in stage.get('options', [])], default=0)
    session_data_dict['path_max_points'] += max_points_in_stage


    for metric in ['detection', 'containment', 'eradication', 'recovery', 'communication']:
        earned = selected_option.get(metric, 0)
        session_data_dict['path_metrics'][metric] += earned

    print(f"DEBUG submit_decision(): Updated metrics: {session_data_dict['path_metrics']}")


    for metric in stage.get('metrics', []):

        max_metric_in_stage = 0
        for option in stage.get('options', []):
            metric_value = option.get(metric, 0)
            if metric_value > max_metric_in_stage:
                max_metric_in_stage = metric_value
        session_data_dict['available_metrics'][metric] += max_metric_in_stage

    print(f"DEBUG submit_decision(): Available metrics: {session_data_dict['available_metrics']}")


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

    if session.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403

    session_data_dict = {}
    if session.session_data:
        try:
            session_data_dict = json.loads(session.session_data)
        except Exception as e:
            print(f"Error parsing session_data: {e}")
            session_data_dict = {}

    scenario_data = scenario_manager.get_scenario(str(session.scenario_id))
    scenario_max_points = scenario_data.get('max_points', 100) if scenario_data else 100

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

    path_total_available = session_data_dict.get('path_max_points', 0)

    print(f"DEBUG complete(): final_score={final_score}, path_total_available={path_total_available}")

    if path_total_available > 0:
        percentage = (final_score / path_total_available) * 100
    else:
        percentage = 0

    print(f"DEBUG complete(): percentage={percentage}")

    percentage = min(100, percentage)

    session.status = 'completed'
    session.completed_at = datetime.utcnow()
    session.score = int(percentage) if isinstance(percentage, (int, float)) else 0

    session.detection_score = int(path_metrics.get('detection', 0))
    session.containment_score = int(path_metrics.get('containment', 0))
    session.eradication_score = int(path_metrics.get('eradication', 0))
    session.recovery_score = int(path_metrics.get('recovery', 0))
    session.communication_score = int(path_metrics.get('communication', 0))

    print(f"DEBUG complete(): path_metrics={path_metrics}")
    print(f"DEBUG complete(): Setting scores - detection={session.detection_score}, containment={session.containment_score}, eradication={session.eradication_score}, recovery={session.recovery_score}, communication={session.communication_score}")

    session_data_dict['path_max_points'] = scenario_max_points
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


    if session.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('scenarios.list'))

    if session.status != 'completed':
        flash('Session not yet completed', 'warning')
        return redirect(url_for('scenarios.play', session_id=session_id))


    print(f"DEBUG results(): session.score={session.score}")
    if session.session_data:
        try:
            session_data_dict = json.loads(session.session_data)
            print(f"DEBUG results(): path_points={session_data_dict.get('path_points')}, path_max_points={session_data_dict.get('path_max_points')}")
            print(f"DEBUG results(): full session_data_dict keys: {session_data_dict.keys()}")
        except Exception:
            pass

    path_metrics_earned = {}
    metrics_max = {}
    path_total_available = 0
    path_points_earned = 0


    scenario_data = scenario_manager.get_scenario(str(session.scenario_id))
    scenario = Scenario(scenario_data) if scenario_data else None

    if session.session_data:
        try:
            session_data_dict = json.loads(session.session_data)
            path_metrics_earned = session_data_dict.get('path_metrics_earned', {})
            metrics_max = session_data_dict.get('metrics_max', {})

            path_total_available = session_data_dict.get('path_total_available', 0)
        except Exception:
            pass


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

    if path_total_available == 0 and scenario:
        path_total_available = scenario.max_points

    return render_template('scenarios/results.html',
                         session=session,
                         scenario=scenario,
                         path_metrics_earned=path_metrics_earned,
                         metrics_max=metrics_max,
                         path_total_available=path_total_available)
