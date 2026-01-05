"""
Routes package
Contains all blueprint definitions
"""

from flask import Blueprint


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
scenario_bp = Blueprint('scenarios', __name__, url_prefix='/scenarios')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


from . import auth, scenarios, admin
