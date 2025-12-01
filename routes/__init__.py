"""
Routes package
Contains all blueprint definitions
"""

from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
scenario_bp = Blueprint('scenarios', __name__, url_prefix='/scenarios')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import route handlers
from . import auth, scenarios, admin