import sqlite3
import jwt
from logger import logger


def get_db_connection(db_path):
    """Create and return a database connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_workspace_details_for_user(db_path, user_id):
    """Fetch workspace details (ID, name, and slug) for a given user."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        query = """
        SELECT w.id, w.name, w.slug
        FROM workspace_users wu
        JOIN workspaces w ON wu.workspace_id = w.id
        WHERE wu.user_id = ?;
        """
        cursor.execute(query, (user_id,))
        workspace_details = [{"workspace_id": row['id'], "workspace_name": row['name'], "workspace_slug": row['slug']}
                             for row in cursor.fetchall()]
    return workspace_details


def validate_parameters(user_id):
    return user_id.isdigit()


def validate_and_decode_jwt(token, jwt_secret_key):
    """Validate and decode the JWT token."""
    try:
        decoded_token = jwt.decode(token, jwt_secret_key, algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
    except jwt.InvalidTokenError:
        logger.error("Invalid token")
    return None


def fetch_first_api_key(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = "SELECT secret FROM api_keys LIMIT 1"
        cursor.execute(query)
        api_key = cursor.fetchone()
        conn.close()

        if api_key:
            return api_key[0]
        else:
            return None
    except sqlite3.Error as error:
        print(f"Error while connecting to sqlite: {error}")
        return None
