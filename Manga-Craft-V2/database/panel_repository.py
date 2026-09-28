from database.database import get_connection


# ============================================================
# SAVE PANEL
# ============================================================

def save_panel(project_id, file_path):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO panels (project_id, file_path)
        VALUES (?, ?)
        """,
        (project_id, file_path)
    )

    conn.commit()

    panel_id = cursor.lastrowid

    conn.close()

    return panel_id


# ============================================================
# GET PANELS FOR PROJECT
# ============================================================

def get_panels(project_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, project_id, file_path, created_at
        FROM panels
        WHERE project_id = ?
        ORDER BY created_at ASC
        """,
        (project_id,)
    )

    panels = cursor.fetchall()

    conn.close()

    return panels


# ============================================================
# GET LATEST PANEL
# ============================================================

def get_latest_panel(project_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, project_id, file_path, created_at
        FROM panels
        WHERE project_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (project_id,)
    )

    panel = cursor.fetchone()

    conn.close()

    return panel


# ============================================================
# DELETE PANEL
# ============================================================

def delete_panel(panel_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM panels
        WHERE id = ?
        """,
        (panel_id,)
    )

    conn.commit()

    conn.close()