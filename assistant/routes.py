from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from assistant.chatbot import chatbot

assistant_bp = Blueprint('assistant', __name__, url_prefix='/api/assistant')


@assistant_bp.route('/message', methods=['POST'])
@login_required
def send_message():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"type": "error", "text": "No data received"}), 400

        action = data.get('action', 'welcome')
        param = data.get('param')

        response = chatbot.handle_action(action, user_id=current_user.id, param=param)
        return jsonify(response), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"type": "error", "text": f"Server error: {str(e)}"}), 500
