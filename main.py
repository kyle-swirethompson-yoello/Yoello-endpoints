import json
import logging
from flask import Flask, request, jsonify
import os
from utils import get_workspace_details_for_user, validate_parameters


app = Flask(__name__)

db_path = os.getenv('DB_PATH', "C:/Users/kyles/PycharmProjects/anything-llm/server/storage/anythingllm.db")

logging.basicConfig(level=logging.INFO,
                    format=json.dumps({'time': '%(asctime)s', 'level': '%(levelname)s', 'message': '%(message)s'}))
logger = logging.getLogger(__name__)


@app.route('/fetch-ai-agents', methods=['GET'])
def fetch_ai_agents():
    user_id = request.args.get('user_id')

    if not validate_parameters(user_id):
        logger.error("Invalid or missing user_id in request parameters")
        return jsonify({"error": "Invalid or missing required parameters: user_id and org_id"}), 400

    try:
        workspace_details = get_workspace_details_for_user(db_path, user_id)
        logger.info(f"Found {len(workspace_details)} accessible workspaces for user_id: {user_id}")
        return jsonify(workspace_details), 200

    except Exception as e:
        logger.error(f"Error fetching workspace details: {e}", exc_info=True)
        return jsonify({"error": "Error fetching workspace details", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
