"""Admin routes - Instructor dashboard and management"""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Scenario, TrainingSession
from werkzeug.security import generate_password_hash
from datetime import datetime
from . import admin_bp

def instructor_required(f):
    """Decorator to require instructor role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in', 'error')
            return redirect(url_for('auth.login'))
        
        if current_user.role != 'instructor':
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
    all_users = User.query.filter_by(role='trainee').all()
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

@admin_bp.route('/scenarios/manage')
@login_required
@instructor_required
def manage_scenarios():
    """Manage scenarios"""
    scenarios = Scenario.query.all()
    return render_template('admin/scenarios.html', scenarios=scenarios)

@admin_bp.route('/scenarios/create', methods=['GET', 'POST'])
@login_required
@instructor_required
def create_scenario():
    """Create new scenario"""
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        difficulty = request.form.get('difficulty_level', 1)
        content = request.form.get('content', '{}')  # JSON string
        
        if not title or not description:
            flash('Title and description are required', 'error')
            return render_template('admin/create_scenario.html')
        
        new_scenario = Scenario(
            title=title,
            description=description,
            difficulty_level=int(difficulty),
            scenario_content=content,
            created_by=current_user.id
        )
        
        try:
            db.session.add(new_scenario)
            db.session.commit()
            flash(f'Scenario "{title}" created successfully!', 'success')
            return redirect(url_for('admin.manage_scenarios'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to create scenario', 'error')
            print(f"Error creating scenario: {e}")
    
    return render_template('admin/create_scenario.html')

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
