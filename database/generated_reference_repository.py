from database.database import get_connection


# ============================================================
# CREATE GENERATED REFERENCE
# ============================================================

def create_generated_reference(
    project_id,
    file_path,
    prompt=None,
    source_panel_id=None
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO generated_references (
            project_id,
            source_panel_id,
            file_path,
            prompt
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            project_id,
            source_panel_id,
            file_path,
            prompt
        )
    )

    conn.commit()

    reference_id = cursor.lastrowid

    conn.close()

    return reference_id


# ============================================================
# GET PROJECT REFERENCES
# ============================================================

def get_generated_references(project_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            project_id,
            source_panel_id,
            file_path,
            prompt,
            created_at
        FROM generated_references
        WHERE project_id = ?
        ORDER BY created_at ASC
        """,
        (project_id,)
    )

    references = cursor.fetchall()

    conn.close()

    return references


# ============================================================
# GET SINGLE REFERENCE
# ============================================================

def get_generated_reference(reference_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            project_id,
            source_panel_id,
            file_path,
            prompt,
            created_at
        FROM generated_references
        WHERE id = ?
        """,
        (reference_id,)
    )

    reference = cursor.fetchone()

    conn.close()

    return reference


# ============================================================
# DELETE REFERENCE
# ============================================================

def delete_generated_reference(reference_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM generated_references
        WHERE id = ?
        """,
        (reference_id,)
    )

    conn.commit()

    conn.close()