import json
import logging
from flask import Flask, request, jsonify
import os
from utils import get_workspace_details_for_user, validate_parameters

# Initialize Flask application
app = Flask(__name__)

# Get database path from environment variable with a default fallback
db_path = os.getenv('DB_PATH', "C:/Users/kyles/PycharmProjects/anything-llm/server/storage/anythingllm.db")

# Setup structured logging for better traceability
logging.basicConfig(level=logging.INFO,
                    format=json.dumps({'time': '%(asctime)s', 'level': '%(levelname)s', 'message': '%(message)s'}))
logger = logging.getLogger(__name__)


@app.route('/fetch-ai-agents', methods=['GET'])
def fetch_ai_agents():
    user_id = request.args.get('user_id')
    org_id = request.args.get('org_id')

    # Validate user_id and org_id parameters
    if not validate_parameters(user_id, org_id):
        logger.error("Invalid or missing user_id or org_id in request parameters")
        return jsonify({"error": "Invalid or missing required parameters: user_id and org_id"}), 400

    try:
        # Fetch workspace details for the user
        workspace_details = get_workspace_details_for_user(db_path, user_id)
        logger.info(f"Found {len(workspace_details)} accessible workspaces for user_id: {user_id}")
        return jsonify(workspace_details), 200

    except Exception as e:
        # Log the error with full traceback for better debugging
        logger.error(f"Error fetching workspace details: {e}", exc_info=True)
        return jsonify({"error": "Error fetching workspace details", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
