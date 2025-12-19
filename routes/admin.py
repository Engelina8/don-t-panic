"""Admin routes - Instructor dashboard and management"""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Scenario, TrainingSession, Group
from scenario_manager import scenario_manager
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from . import admin_bp
from types import SimpleNamespace
from collections import defaultdict
import json

def instructor_required(f):
    """Decorator to require instructor role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in', 'error')
            return redirect(url_for('auth.login'))
        

        if current_user.role not in ('instructor', 'admin'):
            flash('Access denied: Instructor access required', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in', 'error')
            return redirect(url_for('auth.login'))
        
        if current_user.role != 'admin':
            flash('Access denied: Admin access required', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@instructor_required
def dashboard():
    """Instructor dashboard with analytics"""
    

    if current_user.is_admin():

        total_users = User.query.filter_by(role='trainee').count()
        all_scenarios = scenario_manager.get_all_scenarios()
        total_scenarios = len(all_scenarios)
        total_sessions = TrainingSession.query.count()
        completed_sessions = TrainingSession.query.filter_by(status='completed').count()
        

        all_recent = TrainingSession.query.order_by(
            TrainingSession.started_at.desc()
        ).all()
        user_sessions_map = {}
        for session in all_recent:
            if session.user_id not in user_sessions_map:
                user_sessions_map[session.user_id] = session
        recent_sessions = sorted(user_sessions_map.values(), key=lambda s: s.started_at, reverse=True)[:10]
        all_user_sessions = all_recent
    else:

        if current_user.group_id:

            total_users = User.query.filter(
                User.group_id == current_user.group_id,
                User.role == 'trainee'
            ).count()
            

            all_scenarios = scenario_manager.get_all_scenarios()
            total_scenarios = len(all_scenarios)
            

            total_sessions = TrainingSession.query.join(User).filter(
                ((User.group_id == current_user.group_id) & (User.role == 'trainee')) |
                (User.id == current_user.id)
            ).count()
            
            completed_sessions = TrainingSession.query.join(User).filter(
                ((User.group_id == current_user.group_id) & (User.role == 'trainee')) |
                (User.id == current_user.id),
                TrainingSession.status == 'completed'
            ).count()
            

            all_relevant = TrainingSession.query.join(User).filter(
                ((User.group_id == current_user.group_id) & (User.role == 'trainee')) |
                (User.id == current_user.id)
            ).order_by(
                TrainingSession.started_at.desc()
            ).all()
            user_sessions_map = {}
            for session in all_relevant:
                if session.user_id not in user_sessions_map:
                    user_sessions_map[session.user_id] = session
            recent_sessions = sorted(user_sessions_map.values(), key=lambda s: s.started_at, reverse=True)[:10]
            all_user_sessions = all_relevant
        else:

            total_users = 0
            all_scenarios = scenario_manager.get_all_scenarios()
            total_scenarios = len(all_scenarios)
            total_sessions = TrainingSession.query.filter_by(user_id=current_user.id).count()
            completed_sessions = TrainingSession.query.filter(
                TrainingSession.user_id == current_user.id,
                TrainingSession.status == 'completed'
            ).count()
            

            recent_sessions = TrainingSession.query.filter_by(
                user_id=current_user.id
            ).order_by(
                TrainingSession.started_at.desc()
            ).all()
            all_user_sessions = recent_sessions
    
    stats = {
        'total_users': total_users,
        'total_scenarios': total_scenarios,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    }
    
    scenarios_by_id = {}
    all_scenarios_data = scenario_manager.get_all_scenarios()
    for scenario_data in all_scenarios_data:
        scenarios_by_id[scenario_data.get('id')] = scenario_data
    
    scenario_plays = defaultdict(int)
    scenario_avg_scores = defaultdict(lambda: {'total': 0, 'count': 0})
    
    for session in all_user_sessions:
        scenario_plays[session.scenario_id] += 1
        if session.status == 'completed' and session.score is not None:
            scenario_avg_scores[session.scenario_id]['total'] += session.score
            scenario_avg_scores[session.scenario_id]['count'] += 1
    
    scenario_chart_data = []
    for scenario_id, plays in sorted(scenario_plays.items(), key=lambda x: x[1], reverse=True)[:10]:
        if scenario_id not in scenarios_by_id:
            continue
        scenario_title = scenarios_by_id.get(scenario_id, {}).get('title', f'Scenario {scenario_id}')
        avg_score = 0
        if scenario_avg_scores[scenario_id]['count'] > 0:
            avg_score = scenario_avg_scores[scenario_id]['total'] / scenario_avg_scores[scenario_id]['count']
        scenario_chart_data.append({
            'title': scenario_title,
            'plays': plays,
            'avg_score': round(avg_score, 1)
        })
    
    user_scores = defaultdict(lambda: {'total': 0, 'count': 0})
    for session in all_user_sessions:
        if session.status == 'completed' and session.score is not None:
            user = User.query.get(session.user_id)
            user_name = user.username if user else f'User {session.user_id}'
            user_scores[user_name]['total'] += session.score
            user_scores[user_name]['count'] += 1
    
    user_chart_data = []
    for user_name, scores in sorted(user_scores.items(), key=lambda x: x[1]['total']/max(1, x[1]['count']), reverse=True)[:10]:
        avg_score = scores['total'] / max(1, scores['count']) if scores['count'] > 0 else 0
        user_chart_data.append({
            'name': user_name,
            'avg_score': round(avg_score, 1),
            'sessions': scores['count']
        })
    
    completion_data = [
        {'status': 'Completed', 'count': completed_sessions},
        {'status': 'In Progress', 'count': total_sessions - completed_sessions}
    ]
    
    score_distribution = defaultdict(int)
    for session in all_user_sessions:
        if session.status == 'completed' and session.score is not None:
            if session.score >= 90:
                score_distribution['90-100'] += 1
            elif session.score >= 75:
                score_distribution['75-89'] += 1
            elif session.score >= 60:
                score_distribution['60-74'] += 1
            elif session.score >= 40:
                score_distribution['40-59'] += 1
            else:
                score_distribution['0-39'] += 1
    
    score_dist_data = [
        {'range': '0-39', 'count': score_distribution['0-39']},
        {'range': '40-59', 'count': score_distribution['40-59']},
        {'range': '60-74', 'count': score_distribution['60-74']},
        {'range': '75-89', 'count': score_distribution['75-89']},
        {'range': '90-100', 'count': score_distribution['90-100']}
    ]
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_sessions=recent_sessions,
                         all_user_sessions=all_user_sessions,
                         scenarios_by_id=scenarios_by_id,
                         scenario_chart_data=json.dumps(scenario_chart_data),
                         user_chart_data=json.dumps(user_chart_data),
                         completion_data=json.dumps(completion_data),
                         score_dist_data=json.dumps(score_dist_data))

@admin_bp.route('/users')
@login_required
@instructor_required
def users():
    """Manage users"""
    # Show all users for admins, only their group members for instructors
    if current_user.is_admin():
        all_users = User.query.order_by(User.created_at.desc()).all()
    else:
        # Instructors can only see users in their group
        if current_user.group_id:
            all_users = User.query.filter(
                User.group_id == current_user.group_id,
                User.role.in_(['trainee', 'instructor'])
            ).order_by(User.created_at.desc()).all()
        else:
            # Instructor not in a group sees no users
            all_users = []
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/users/add', methods=['POST'])
@login_required
@instructor_required
def add_user():
    """Add a new user directly"""
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', 'trainee')
    

    if not username or not email or not password:
        flash('Username, email, and password are required', 'error')
        return redirect(url_for('admin.users'))
    
    if len(password) < 6:
        flash('Password must be at least 6 characters long', 'error')
        return redirect(url_for('admin.users'))
    

    if User.find_by_username(username):
        flash(f'Username "{username}" already exists', 'error')
        return redirect(url_for('admin.users'))
    
    if User.find_by_email(email):
        flash(f'Email "{email}" already registered', 'error')
        return redirect(url_for('admin.users'))
    

    valid_roles = ['trainee', 'instructor']
    if current_user.is_admin():
        valid_roles.append('admin')
    
    if role not in valid_roles:
        flash('Invalid role selected', 'error')
        return redirect(url_for('admin.users'))
    

    if role == 'admin' and not current_user.is_admin():
        flash('Only administrators can create admin users', 'error')
        return redirect(url_for('admin.users'))
    
    try:

        new_user = User(
            username=username,
            email=email,
            role=role,
            is_active=True
        )
        new_user.set_password(password)
        

        if current_user.role == 'instructor' and current_user.group_id:
            new_user.group_id = current_user.group_id
        
        db.session.add(new_user)
        db.session.commit()
        
        role_display = 'Admin' if role == 'admin' else ('Instructor' if role == 'instructor' else 'Trainee')
        group_msg = f' and added to your group' if current_user.role == 'instructor' and current_user.group_id else ''
        flash(f'✅ User "{username}" created successfully as {role_display}{group_msg}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error creating user: {str(e)}', 'error')
    
    return redirect(url_for('admin.users'))

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
    
    # Load scenario data for display
    scenarios_by_id = {}
    all_scenarios_data = scenario_manager.get_all_scenarios()
    for scenario_data in all_scenarios_data:
        scenarios_by_id[scenario_data.get('id')] = scenario_data
    
    return render_template('admin/user_detail.html',
                         user=user,
                         sessions=sessions,
                         stats=user_stats,
                         scenarios_by_id=scenarios_by_id)

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

@admin_bp.route('/users/<int:user_id>/reset-logs', methods=['POST'])
@login_required
@instructor_required
def reset_user_logs(user_id):
    """Reset all training logs for a user"""
    user = User.query.get_or_404(user_id)
    
    try:
        # Delete all training sessions for this user
        TrainingSession.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'All training logs for "{user.username}" have been reset'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/scenarios/create-folder', methods=['POST'])
@login_required
@instructor_required
def create_folder():
    """Create a new scenario folder"""
    import json
    from pathlib import Path
    

    if request.is_json:
        data = request.get_json()
        folder_name = data.get('folder_name', '').strip()
    else:
        folder_name = request.form.get('folder_name', '').strip()
    
    if not folder_name:
        if request.is_json:
            return jsonify({'error': 'Folder name cannot be empty'}), 400
        flash('Folder name cannot be empty', 'error')
        return redirect(url_for('admin.manage_scenarios'))
    

    if not folder_name.replace('_', '').replace('-', '').isalnum():
        if request.is_json:
            return jsonify({'error': 'Folder name can only contain letters, numbers, dashes, and underscores'}), 400
        flash('Folder name can only contain letters, numbers, dashes, and underscores', 'error')
        return redirect(url_for('admin.manage_scenarios'))
    
    try:
        scenarios_dir = Path('scenarios')
        new_folder = scenarios_dir / folder_name
        

        if new_folder.exists():
            if request.is_json:
                return jsonify({'error': 'Folder already exists'}), 409
            flash('Folder already exists', 'error')
        else:
            new_folder.mkdir(exist_ok=True)
            if request.is_json:
                return jsonify({'success': True, 'message': f'Folder "{folder_name}" created successfully'})
            flash(f'✅ Folder "{folder_name}" created successfully', 'success')
    except Exception as e:
        if request.is_json:
            return jsonify({'error': f'Error creating folder: {str(e)}'}), 500
        flash(f'❌ Error creating folder: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_scenarios'))

@admin_bp.route('/scenarios/manage')
@login_required
@instructor_required
def manage_scenarios():
    """Manage scenarios"""
    scenarios_data = scenario_manager.get_all_scenarios()
    scenarios = []
    
    # Get all sessions for statistics
    all_sessions = TrainingSession.query.filter_by(status='completed').all()
    
    for data in scenarios_data:
        scenario = Scenario(data)
        
        # Calculate times_played and average_score from database
        scenario_sessions = [s for s in all_sessions if str(s.scenario_id) == str(scenario.id)]
        scenario.times_played = len(scenario_sessions)
        
        if scenario_sessions:
            scores = [s.score for s in scenario_sessions if s.score]
            scenario.average_score = (sum(scores) / len(scores)) if scores else 0
        else:
            scenario.average_score = None
        
        scenarios.append(scenario)
    
    categories = scenario_manager.get_categories()
    
    return render_template('admin/scenarios.html', 
                         scenarios=scenarios,
                         categories=categories)

@admin_bp.route('/scenarios/create', methods=['GET', 'POST'])
@login_required
@instructor_required
def create_scenario():
    """Create new scenario"""
    categories = scenario_manager.get_categories()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        incident_type = request.form.get('incident_type', 'ransomware')
        difficulty = request.form.get('difficulty_level', 3)
        estimated_time = request.form.get('estimated_time', 30)
        max_points = request.form.get('max_points', 100)
        category = request.form.get('category', '')
        auto_max_points = request.form.get('auto_max_points') == 'on'
        scenario_content = request.form.get('scenario_content', '{}')
        

        if not title or not description or not scenario_content:
            flash('Title, description, and scenario content are required', 'error')
            return render_template('admin/create_scenario.html', 
                                 scenario=request.form,
                                 categories=categories)
        
        try:

            import json
            scenario_data = json.loads(scenario_content)
            

            if auto_max_points:
                total_points = 0
                if 'stages' in scenario_data:
                    for stage in scenario_data['stages']:
                        if 'options' in stage:
                            max_stage_points = 0
                            for option in stage['options']:
                                points = int(option.get('points', 0))
                                if points > max_stage_points:
                                    max_stage_points = points
                            total_points += max_stage_points
                max_points = total_points if total_points > 0 else 100
            

            complete_scenario_data = {
                'title': title,
                'description': description,
                'category': category,
                'incident_type': incident_type,
                'difficulty_level': int(difficulty),
                'estimated_time': int(estimated_time),
                'max_points': int(max_points),
                'scenario_content': scenario_data,
                'created_by': current_user.id,
                'is_active': True
            }
            

            created_scenario = scenario_manager.create_scenario(complete_scenario_data, category)
            
            flash(f'✅ Scenario "{title}" created successfully! (Max Points: {max_points})', 'success')
            return redirect(url_for('admin.manage_scenarios'))
            
        except json.JSONDecodeError as e:
            flash(f'❌ Invalid JSON in scenario content: {str(e)}', 'error')
            return render_template('admin/create_scenario.html', 
                                 scenario=request.form,
                                 categories=categories)
        except Exception as e:
            flash(f'❌ Failed to create scenario: {str(e)}', 'error')
            print(f"Error creating scenario: {e}")
            return render_template('admin/create_scenario.html', 
                                 scenario=request.form,
                                 categories=categories)
    

    default_scenario = SimpleNamespace(
        scenario_content='{}',
        title='',
        description='',
        category='',
        incident_type='ransomware',
        difficulty_level=3,
        estimated_time=30,
        max_points=100
    )
    
    return render_template('admin/create_scenario.html', 
                         scenario=default_scenario,
                         categories=categories)

@admin_bp.route('/scenarios/<scenario_id>/edit', methods=['GET', 'POST'])
@login_required
@instructor_required
def edit_scenario(scenario_id):
    """Edit an existing scenario"""
    scenario_data = scenario_manager.get_scenario(scenario_id)
    
    if not scenario_data:
        flash('Scenario not found', 'error')
        return redirect(url_for('admin.manage_scenarios'))
    
    categories = scenario_manager.get_categories()
    
    if request.method == 'POST':
        title = request.form.get('title', scenario_data.get('title'))
        description = request.form.get('description', scenario_data.get('description'))
        incident_type = request.form.get('incident_type', scenario_data.get('incident_type'))
        difficulty = int(request.form.get('difficulty_level', scenario_data.get('difficulty_level', 3)))
        estimated_time = int(request.form.get('estimated_time', scenario_data.get('estimated_time', 30)))
        category = request.form.get('category', scenario_data.get('category', ''))
        auto_max_points = request.form.get('auto_max_points') == 'on'
        scenario_content = request.form.get('scenario_content', '{}')
        
        try:
            # Validate JSON
            import json
            scenario_json = json.loads(scenario_content)
            
            # Calculate max_points if auto is enabled
            if auto_max_points:
                total_points = 0
                if 'stages' in scenario_json:
                    for stage in scenario_json['stages']:
                        if 'options' in stage:
                            max_stage_points = 0
                            for option in stage['options']:
                                points = int(option.get('points', 0))
                                if points > max_stage_points:
                                    max_stage_points = points
                            total_points += max_stage_points
                max_points = total_points if total_points > 0 else 100
            else:
                max_points = int(request.form.get('max_points', scenario_data.get('max_points', 100)))
            
            # Create updated scenario data
            updated_scenario = {
                'id': scenario_id,
                'title': title,
                'description': description,
                'category': category,
                'incident_type': incident_type,
                'difficulty_level': difficulty,
                'estimated_time': estimated_time,
                'max_points': max_points,
                'scenario_content': scenario_json,
                'created_by': scenario_data.get('created_by'),
                'created_at': scenario_data.get('created_at'),
                'is_active': scenario_data.get('is_active', True)
            }
            
            # Update the scenario file
            scenario_manager.update_scenario(scenario_id, updated_scenario)
            
            flash(f'✅ Scenario "{title}" updated successfully! (Max Points: {max_points})', 'success')
            return redirect(url_for('admin.manage_scenarios'))
            
        except json.JSONDecodeError as e:
            flash(f'❌ Invalid JSON in scenario content: {str(e)}', 'error')
            scenario = Scenario(scenario_data)
            return render_template('admin/create_scenario.html', 
                                 scenario=scenario,
                                 categories=categories)
        except Exception as e:
            flash(f'❌ Failed to update scenario: {str(e)}', 'error')
            scenario = Scenario(scenario_data)
            return render_template('admin/create_scenario.html', 
                                 scenario=scenario,
                                 categories=categories)
    
    scenario = Scenario(scenario_data)
    return render_template('admin/create_scenario.html', 
                         scenario=scenario,
                         categories=categories)

@admin_bp.route('/scenarios/<scenario_id>/delete', methods=['POST'])
@login_required
@instructor_required
def delete_scenario(scenario_id):
    """Delete a scenario"""
    scenario_data = scenario_manager.get_scenario(scenario_id)
    
    if not scenario_data:
        return jsonify({'success': False, 'error': 'Scenario not found'}), 404
    
    title = scenario_data.get('title', 'Unknown')
    
    try:
        scenario_manager.delete_scenario(scenario_id)
        flash(f'Scenario "{title}" has been deleted', 'success')
        return jsonify({'success': True, 'redirect': url_for('admin.manage_scenarios')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/reports')
@login_required
@instructor_required
def reports():
    """View training reports and analytics"""
    
    # Get all completed sessions with statistics
    completed_sessions = TrainingSession.query.filter_by(status='completed').all()
    
    # Load scenario data for display
    scenarios_by_id = {}
    all_scenarios_data = scenario_manager.get_all_scenarios()
    
    # Scenario performance
    scenario_stats = {}
    for scenario_data in all_scenarios_data:
        scenario_id = scenario_data.get('id')
        scenarios_by_id[scenario_id] = scenario_data
        scenario = Scenario(scenario_data)
        sessions = [s for s in completed_sessions if str(s.scenario_id) == str(scenario_id)]
        if sessions:
            scenario_stats[scenario.title] = {
                'attempts': len(sessions),
                'avg_score': sum([s.score for s in sessions if s.score]) / len(sessions)
            }
    
    return render_template('admin/reports.html',
                         completed_sessions=completed_sessions,
                         scenario_stats=scenario_stats,
                         scenarios_by_id=scenarios_by_id)


# ========================
# GROUP MANAGEMENT ROUTES (Admin only)
# ========================

@admin_bp.route('/groups')
@login_required
@admin_required
def groups():
    """Manage groups (admin only)"""
    all_groups = Group.query.order_by(Group.created_at.desc()).all()
    return render_template('admin/groups.html', groups=all_groups)

@admin_bp.route('/groups/add', methods=['POST'])
@login_required
@admin_required
def add_group():
    """Create a new group"""
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not name:
        flash('Group name is required', 'error')
        return redirect(url_for('admin.groups'))
    
    # Check if group already exists
    if Group.query.filter_by(name=name).first():
        flash(f'Group "{name}" already exists', 'error')
        return redirect(url_for('admin.groups'))
    
    try:
        new_group = Group(
            name=name,
            description=description,
            created_by=current_user.id
        )
        db.session.add(new_group)
        db.session.commit()
        flash(f'Group "{name}" created successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating group: {str(e)}', 'error')
    
    return redirect(url_for('admin.groups'))

@admin_bp.route('/groups/<int:id>')
@login_required
@admin_required
def view_group(id):
    """View group details and manage members"""
    group = Group.query.get_or_404(id)
    

    from sqlalchemy import or_
    available_users = User.query.filter(
        or_(User.group_id == None, User.group_id != id),
        User.role.in_(['trainee', 'instructor'])
    ).order_by(User.username).all()
    
    return render_template('admin/group_detail.html', 
                         group=group,
                         available_users=available_users)

@admin_bp.route('/groups/<int:id>/add-member', methods=['POST'])
@login_required
@admin_required
def add_group_member(id):
    """Add a member to a group"""
    group = Group.query.get_or_404(id)
    user_id = request.form.get('user_id', type=int)
    
    if not user_id:
        flash('Please select a user', 'error')
        return redirect(url_for('admin.view_group', id=id))
    
    user = User.query.get_or_404(user_id)
    
    # Check if user already in a group
    if user.group_id:
        flash(f'{user.username} is already in a group', 'error')
        return redirect(url_for('admin.view_group', id=id))
    
    try:
        user.group_id = id
        db.session.commit()
        flash(f'{user.username} added to {group.name}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding member: {str(e)}', 'error')
    
    return redirect(url_for('admin.view_group', id=id))

@admin_bp.route('/groups/<int:group_id>/remove-member/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def remove_group_member(group_id, user_id):
    """Remove a member from a group"""
    group = Group.query.get_or_404(group_id)
    user = User.query.get_or_404(user_id)
    
    if user.group_id != group_id:
        flash('User is not in this group', 'error')
        return redirect(url_for('admin.view_group', id=group_id))
    
    try:
        user.group_id = None
        db.session.commit()
        flash(f'{user.username} removed from {group.name}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing member: {str(e)}', 'error')
    
    return redirect(url_for('admin.view_group', id=group_id))

@admin_bp.route('/groups/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_group(id):
    """Delete a group"""
    group = Group.query.get_or_404(id)
    
    # Remove group association from all members
    members = group.members.all()
    for member in members:
        member.group_id = None
    
    try:
        db.session.delete(group)
        db.session.commit()
        flash(f'Group "{group.name}" deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting group: {str(e)}', 'error')
    
    return redirect(url_for('admin.groups'))
