"""Admin routes - Instructor dashboard and management"""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Scenario, TrainingSession
from werkzeug.security import generate_password_hash
from datetime import datetime
from . import admin_bp
from types import SimpleNamespace

def instructor_required(f):
    """Decorator to require instructor role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in', 'error')
            return redirect(url_for('auth.login'))
        
        # Allow both 'instructor' and 'admin' roles to access instructor routes
        if current_user.role not in ('instructor', 'admin'):
            flash('Access denied: Instructor access required', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@instructor_required
def dashboard():
    """Instructor dashboard"""
    
    # Get statistics
    total_users = User.query.filter_by(role='trainee').count()
    total_scenarios = Scenario.query.count()
    total_sessions = TrainingSession.query.count()
    completed_sessions = TrainingSession.query.filter_by(status='completed').count()
    
    # Get recent activity
    recent_sessions = TrainingSession.query.order_by(
        TrainingSession.started_at.desc()
    ).limit(10).all()
    
    stats = {
        'total_users': total_users,
        'total_scenarios': total_scenarios,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    }
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_sessions=recent_sessions)

@admin_bp.route('/users')
@login_required
@instructor_required
def users():
    """Manage users"""
    all_users = User.query.filter_by(role='trainee').order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/users/<int:user_id>')
@login_required
@instructor_required
def user_detail(user_id):
    """View user details and progress"""
    user = User.query.get_or_404(user_id)
    
    # Get user's training history
    sessions = TrainingSession.query.filter_by(user_id=user_id).order_by(
        TrainingSession.started_at.desc()
    ).all()
    
    # Calculate statistics
    total_sessions = len(sessions)
    completed_sessions = len([s for s in sessions if s.status == 'completed'])
    average_score = sum([s.score for s in sessions if s.score]) / completed_sessions if completed_sessions > 0 else 0
    
    user_stats = {
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'average_score': average_score
    }
    
    return render_template('admin/user_detail.html',
                         user=user,
                         sessions=sessions,
                         stats=user_stats)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@instructor_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    username = user.username
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': f'User "{username}" deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/scenarios/manage')
@login_required
@instructor_required
def manage_scenarios():
    """Manage scenarios"""
    scenarios = Scenario.query.order_by(Scenario.created_at.desc()).all()
    return render_template('admin/scenarios.html', scenarios=scenarios)

@admin_bp.route('/scenarios/create', methods=['GET', 'POST'])
@login_required
@instructor_required
def create_scenario():
    """Create new scenario"""
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        incident_type = request.form.get('incident_type', 'ransomware')
        difficulty = request.form.get('difficulty_level', 3)
        estimated_time = request.form.get('estimated_time', 30)
        max_points = request.form.get('max_points', 100)
        scenario_content = request.form.get('scenario_content', '{}')
        
        # Validation
        if not title or not description or not scenario_content:
            flash('Title, description, and scenario content are required', 'error')
            # Re-render the form with submitted values so the template has `scenario` defined
            return render_template('admin/create_scenario.html', scenario=request.form)
        
        try:
            # Validate JSON
            import json
            json.loads(scenario_content)
            
            new_scenario = Scenario(
                title=title,
                description=description,
                incident_type=incident_type,
                difficulty_level=int(difficulty),
                estimated_time=int(estimated_time),
                max_points=int(max_points),
                scenario_content=scenario_content,
                created_by=current_user.id
            )
            
            db.session.add(new_scenario)
            db.session.commit()
            flash(f'✅ Scenario "{title}" created successfully!', 'success')
            return redirect(url_for('admin.manage_scenarios'))
            
        except json.JSONDecodeError as e:
            flash(f'❌ Invalid JSON in scenario content: {str(e)}', 'error')
            return render_template('admin/create_scenario.html', 
                                 scenario=request.form)
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Failed to create scenario: {str(e)}', 'error')
            print(f"Error creating scenario: {e}")
            return render_template('admin/create_scenario.html', scenario=request.form)
    
    # Provide a safe default `scenario` object for the template so attribute
    # access like `scenario.scenario_content` does not raise UndefinedError
    default_scenario = SimpleNamespace(
        scenario_content='{}',
        title='',
        description='',
        incident_type='ransomware',
        difficulty_level=3,
        estimated_time=30,
        max_points=100
    )

    return render_template('admin/create_scenario.html', scenario=default_scenario)

@admin_bp.route('/scenarios/<int:scenario_id>/edit', methods=['GET', 'POST'])
@login_required
@instructor_required
def edit_scenario(scenario_id):
    """Edit an existing scenario"""
    scenario = Scenario.query.get_or_404(scenario_id)
    
    if request.method == 'POST':
        scenario.title = request.form.get('title', scenario.title)
        scenario.description = request.form.get('description', scenario.description)
        scenario.incident_type = request.form.get('incident_type', scenario.incident_type)
        scenario.difficulty_level = int(request.form.get('difficulty_level', scenario.difficulty_level))
        scenario.estimated_time = int(request.form.get('estimated_time', scenario.estimated_time))
        scenario.max_points = int(request.form.get('max_points', scenario.max_points or 100))
        scenario.scenario_content = request.form.get('scenario_content', scenario.scenario_content)
        scenario.updated_at = datetime.utcnow()
        
        try:
            # Validate JSON
            import json
            json.loads(scenario.scenario_content)
            
            db.session.commit()
            flash(f'✅ Scenario "{scenario.title}" updated successfully!', 'success')
            return redirect(url_for('admin.manage_scenarios'))
            
        except json.JSONDecodeError as e:
            db.session.rollback()
            flash(f'❌ Invalid JSON in scenario content: {str(e)}', 'error')
            return render_template('admin/create_scenario.html', scenario=scenario)
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Failed to update scenario: {str(e)}', 'error')
            return render_template('admin/create_scenario.html', scenario=scenario)
    
    return render_template('admin/create_scenario.html', scenario=scenario)

@admin_bp.route('/scenarios/<int:scenario_id>/delete', methods=['POST'])
@login_required
@instructor_required
def delete_scenario(scenario_id):
    """Delete a scenario"""
    scenario = Scenario.query.get_or_404(scenario_id)
    title = scenario.title
    
    try:
        db.session.delete(scenario)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Scenario "{title}" deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/reports')
@login_required
@instructor_required
def reports():
    """View training reports and analytics"""
    
    # Get all completed sessions with statistics
    completed_sessions = TrainingSession.query.filter_by(status='completed').all()
    
    # Scenario performance
    scenario_stats = {}
    for scenario in Scenario.query.all():
        sessions = [s for s in completed_sessions if s.scenario_id == scenario.id]
        if sessions:
            scenario_stats[scenario.title] = {
                'attempts': len(sessions),
                'avg_score': sum([s.score for s in sessions if s.score]) / len(sessions)
            }
    
    return render_template('admin/reports.html',
                         completed_sessions=completed_sessions,
                         scenario_stats=scenario_stats)
