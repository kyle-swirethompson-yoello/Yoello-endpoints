import sqlite3


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
