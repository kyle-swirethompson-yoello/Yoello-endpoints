import json
import logging
import jwt
import requests
from flask import Flask, request, jsonify
import os
from utils import get_workspace_details_for_user, validate_parameters

app = Flask(__name__)

db_path = os.getenv('DB_PATH', "C:/Users/kyles/PycharmProjects/anything-llm/server/storage/anythingllm.db")
instance_path = os.getenv('ALLM_URL', "localhost:3001")
instance_apikey = os.getenv('ALLM_APIKEY', "X92NGQB-S03M9N6-JBWDSSB-BPMKG88")
jwt_secret_key = os.getenv('JWT_SECRET', "secret")
logging.basicConfig(level=logging.INFO,
                    format=json.dumps({'time': '%(asctime)s', 'level': '%(levelname)s', 'message': '%(message)s'}))
logger = logging.getLogger(__name__)


def validate_and_decode_jwt(token):
    """Validate and decode the JWT token."""
    try:
        decoded_token = jwt.decode(token, jwt_secret_key, algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
    except jwt.InvalidTokenError:
        logger.error("Invalid token")
    return None


@app.route('/chat-with-ai-agents', methods=['POST'])
def chat_with_ai_agent():
    """Endpoint to chat with AI agents."""
    auth_header = request.headers.get('Authorization', '')
    bearer_token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else None
    if not bearer_token:
        logger.error("No bearer token provided")
        return jsonify({"error": "Authorization header missing or not in Bearer token format"}), 401

    decoded_token = validate_and_decode_jwt(bearer_token)
    if not decoded_token:
        logger.error("Failed to validate or decode JWT token")
        return jsonify({"error": "Invalid or expired token"}), 401
    data = request.json
    ai_agent_slug = data.get('aiAgent')
    query = data.get('query')
    mode = data.get('mode')
    sourceAttribution = data.get('sourceAttribution')
    logger.info(f"Received chat request for AI agent: {ai_agent_slug} with query: {query}")

    url = f"http://{instance_path}/api/v1/workspace/{ai_agent_slug}/chat"
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {instance_apikey}',
        'Content-Type': 'application/json'
    }
    payload = {
        "message": query,
        "mode": mode
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
        if not sourceAttribution:
            del response_data['sources']
        logger.info(f"Successfully received response from AI agent: {ai_agent_slug}")
        return jsonify(response_data)
    except requests.RequestException as e:
        logger.error(f"Error while chatting with AI agent: {ai_agent_slug}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/fetch-ai-agents', methods=['GET'])
def fetch_ai_agents():
    """Endpoint to fetch AI agents."""
    auth_header = request.headers.get('Authorization', '')
    bearer_token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else None
    if not bearer_token:
        logger.error("No bearer token provided")
        return jsonify({"error": "Authorization header missing or not in Bearer token format"}), 401

    decoded_token = validate_and_decode_jwt(bearer_token)
    if not decoded_token:
        logger.error("Failed to validate or decode JWT token")
        return jsonify({"error": "Invalid or expired token"}), 401
    user_id = str(decoded_token.get('user_id'))
    if not validate_parameters(user_id):
        logger.error("Invalid or missing user_id in request parameters")
        return jsonify({"error": "Invalid or missing required parameters: user_id"}), 400

    try:
        workspace_details = get_workspace_details_for_user(db_path, user_id)
        logger.info(
            f"Successfully fetched workspace details for user_id: {user_id}, found {len(workspace_details)} workspaces")
        return jsonify(workspace_details), 200
    except Exception as e:
        logger.error(f"Error fetching workspace details for user_id: {user_id}", exc_info=True)
        return jsonify({"error": "Error fetching workspace details", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
