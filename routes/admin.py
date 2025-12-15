"""Admin routes - Instructor dashboard and management"""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Scenario, TrainingSession, Group
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
    """Instructor dashboard"""
    
    # Get statistics and recent activity based on user hierarchy
    if current_user.is_admin():
        # ADMIN: Can see ALL users and sessions
        total_users = User.query.filter_by(role='trainee').count()
        total_scenarios = Scenario.query.count()
        total_sessions = TrainingSession.query.count()
        completed_sessions = TrainingSession.query.filter_by(status='completed').count()
        
        # Get all recent activity
        recent_sessions = TrainingSession.query.order_by(
            TrainingSession.started_at.desc()
        ).limit(10).all()
    else:
        # INSTRUCTOR: Can see their own sessions + trainee sessions in their group (NO ADMINS)
        if current_user.group_id:
            # Count trainees in their group
            total_users = User.query.filter(
                User.group_id == current_user.group_id,
                User.role == 'trainee'
            ).count()
            
            # Total scenarios (available to all)
            total_scenarios = Scenario.query.count()
            
            # Sessions from: trainees in their group OR their own
            total_sessions = TrainingSession.query.join(User).filter(
                ((User.group_id == current_user.group_id) & (User.role == 'trainee')) |
                (User.id == current_user.id)
            ).count()
            
            completed_sessions = TrainingSession.query.join(User).filter(
                ((User.group_id == current_user.group_id) & (User.role == 'trainee')) |
                (User.id == current_user.id),
                TrainingSession.status == 'completed'
            ).count()
            
            # Recent activity from: trainees in their group OR their own
            recent_sessions = TrainingSession.query.join(User).filter(
                ((User.group_id == current_user.group_id) & (User.role == 'trainee')) |
                (User.id == current_user.id)
            ).order_by(
                TrainingSession.started_at.desc()
            ).limit(10).all()
        else:
            # Instructor not in a group sees only their own data
            total_users = 0
            total_scenarios = Scenario.query.count()
            total_sessions = TrainingSession.query.filter_by(user_id=current_user.id).count()
            completed_sessions = TrainingSession.query.filter(
                TrainingSession.user_id == current_user.id,
                TrainingSession.status == 'completed'
            ).count()
            
            # Recent activity from their own sessions
            recent_sessions = TrainingSession.query.filter_by(
                user_id=current_user.id
            ).order_by(
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
    
    # Validation
    if not username or not email or not password:
        flash('Username, email, and password are required', 'error')
        return redirect(url_for('admin.users'))
    
    if len(password) < 6:
        flash('Password must be at least 6 characters long', 'error')
        return redirect(url_for('admin.users'))
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        flash(f'Username "{username}" already exists', 'error')
        return redirect(url_for('admin.users'))
    
    if User.query.filter_by(email=email).first():
        flash(f'Email "{email}" already registered', 'error')
        return redirect(url_for('admin.users'))
    
    # Validate role - only admins can create admin users
    valid_roles = ['trainee', 'instructor']
    if current_user.is_admin():
        valid_roles.append('admin')
    
    if role not in valid_roles:
        flash('Invalid role selected', 'error')
        return redirect(url_for('admin.users'))
    
    # Only admins can create other admins
    if role == 'admin' and not current_user.is_admin():
        flash('Only administrators can create admin users', 'error')
        return redirect(url_for('admin.users'))
    
    try:
        # Create new user
        new_user = User(
            username=username,
            email=email,
            role=role,
            is_active=True
        )
        new_user.set_password(password)
        
        # Auto-assign to instructor's group if created by an instructor
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
        auto_max_points = request.form.get('auto_max_points') == 'on'
        scenario_content = request.form.get('scenario_content', '{}')
        
        # Validation
        if not title or not description or not scenario_content:
            flash('Title, description, and scenario content are required', 'error')
            # Re-render the form with submitted values so the template has `scenario` defined
            return render_template('admin/create_scenario.html', scenario=request.form)
        
        try:
            # Validate JSON
            import json
            scenario_data = json.loads(scenario_content)
            
            # Calculate max_points if auto is enabled
            if auto_max_points:
                total_points = 0
                if 'stages' in scenario_data:
                    for stage in scenario_data['stages']:
                        # Sum the HIGHEST points from each stage (best answer path)
                        if 'options' in stage:
                            max_stage_points = 0
                            for option in stage['options']:
                                points = int(option.get('points', 0))
                                if points > max_stage_points:
                                    max_stage_points = points
                            total_points += max_stage_points
                max_points = total_points if total_points > 0 else 100
            
            # Inject metadata into scenario_data
            scenario_data['title'] = title
            scenario_data['description'] = description
            scenario_data['incident_type'] = incident_type
            scenario_data['difficulty_level'] = int(difficulty)
            scenario_data['estimated_time'] = int(estimated_time)
            scenario_data['max_points'] = int(max_points)
            
            # Convert back to JSON string
            scenario_content = json.dumps(scenario_data, indent=2)
            
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
            flash(f'✅ Scenario "{title}" created successfully! (Max Points: {max_points})', 'success')
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
        auto_max_points = request.form.get('auto_max_points') == 'on'
        scenario.scenario_content = request.form.get('scenario_content', scenario.scenario_content)
        scenario.updated_at = datetime.utcnow()
        
        try:
            # Validate JSON
            import json
            scenario_data = json.loads(scenario.scenario_content)
            
            # Calculate max_points if auto is enabled
            if auto_max_points:
                total_points = 0
                if 'stages' in scenario_data:
                    for stage in scenario_data['stages']:
                        # Sum the HIGHEST points from each stage (best answer path)
                        if 'options' in stage:
                            max_stage_points = 0
                            for option in stage['options']:
                                points = int(option.get('points', 0))
                                if points > max_stage_points:
                                    max_stage_points = points
                            total_points += max_stage_points
                scenario.max_points = total_points if total_points > 0 else 100
            else:
                scenario.max_points = int(request.form.get('max_points', scenario.max_points or 100))
            
            # Inject metadata into scenario_data
            scenario_data['title'] = scenario.title
            scenario_data['description'] = scenario.description
            scenario_data['incident_type'] = scenario.incident_type
            scenario_data['difficulty_level'] = scenario.difficulty_level
            scenario_data['estimated_time'] = scenario.estimated_time
            scenario_data['max_points'] = scenario.max_points
            
            # Convert back to JSON string
            scenario.scenario_content = json.dumps(scenario_data, indent=2)
            
            db.session.commit()
            flash(f'✅ Scenario "{scenario.title}" updated successfully! (Max Points: {scenario.max_points})', 'success')
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
        flash(f'Scenario "{title}" has been deleted', 'success')
        return jsonify({'success': True, 'redirect': url_for('admin.manage_scenarios')})
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
    
    # Get all users not in this group (including those with no group)
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
