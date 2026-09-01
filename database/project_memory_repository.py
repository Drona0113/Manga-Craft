from database.database import get_connection


# ============================================================
# SAVE PROJECT MEMORY
# ============================================================

def save_project_memory(
    project_id,
    memory_type,
    content,
    asset_id=None
):
    """
    Save a project memory.

    If the exact same memory already exists for the same
    project, memory type, and asset, do not create a duplicate.
    """

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------------------------
    # CHECK FOR EXISTING MEMORY
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM project_memory
        WHERE project_id = ?
          AND memory_type = ?
          AND content = ?
          AND (
              asset_id = ?
              OR (asset_id IS NULL AND ? IS NULL)
          )
        LIMIT 1
        """,
        (
            project_id,
            memory_type,
            content,
            asset_id,
            asset_id
        )
    )

    existing = cursor.fetchone()

    # --------------------------------------------------------
    # DUPLICATE
    # --------------------------------------------------------

    if existing:

        cursor.execute(
            """
            UPDATE project_memory
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (existing["id"],)
        )

        conn.commit()
        conn.close()

        return {
            "status": "already_exists",
            "id": existing["id"]
        }

    # --------------------------------------------------------
    # CREATE MEMORY
    # --------------------------------------------------------

    cursor.execute(
        """
        INSERT INTO project_memory (
            project_id,
            memory_type,
            content,
            asset_id
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            project_id,
            memory_type,
            content,
            asset_id
        )
    )

    memory_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "status": "created",
        "id": memory_id
    }


# ============================================================
# GET PROJECT MEMORY
# ============================================================

def get_project_memory(
    project_id,
    memory_type=None
):
    """
    Retrieve project memories.

    If memory_type is provided, only that category is returned.
    """

    conn = get_connection()
    cursor = conn.cursor()

    if memory_type:

        cursor.execute(
            """
            SELECT
                id,
                project_id,
                memory_type,
                content,
                asset_id,
                created_at,
                updated_at
            FROM project_memory
            WHERE project_id = ?
              AND memory_type = ?
            ORDER BY updated_at DESC
            """,
            (
                project_id,
                memory_type
            )
        )

    else:

        cursor.execute(
            """
            SELECT
                id,
                project_id,
                memory_type,
                content,
                asset_id,
                created_at,
                updated_at
            FROM project_memory
            WHERE project_id = ?
            ORDER BY updated_at DESC
            """,
            (project_id,)
        )

    memories = cursor.fetchall()

    conn.close()

    return memories


# ============================================================
# SEARCH PROJECT MEMORY
# ============================================================

# ============================================================
# SEARCH PROJECT MEMORY
# ============================================================

def search_project_memory(
    project_id,
    query
):
    """
    Search project memories using SQLite text matching.

    Each meaningful word in the query is searched independently.
    Results matching more query terms are returned first.
    """

    conn = get_connection()
    cursor = conn.cursor()

    words = [
        word.strip(".,!?;:'\"()[]{}")
        for word in query.lower().split()
        if len(word.strip(".,!?;:'\"()[]{}")) > 1
    ]

    if not words:
        conn.close()
        return []

    conditions = []
    parameters = [project_id]

    for word in words:
        conditions.append(
            "LOWER(content) LIKE ?"
        )
        parameters.append(f"%{word}%")

    where_clause = " OR ".join(conditions)

    cursor.execute(
        f"""
        SELECT
            id,
            project_id,
            memory_type,
            content,
            asset_id,
            created_at,
            updated_at
        FROM project_memory
        WHERE project_id = ?
          AND ({where_clause})
        ORDER BY updated_at DESC
        """,
        parameters
    )

    memories = cursor.fetchall()

    conn.close()

    return memories




# ============================================================
# GET PROJECT CONTEXT
# ============================================================

def get_project_context(project_id):
    """
    Retrieve all project information useful for LLM context.
    """

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------------------------
    # PROJECT
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            id,
            name,
            created_at,
            updated_at,
            last_opened
        FROM projects
        WHERE id = ?
        """,
        (project_id,)
    )

    project = cursor.fetchone()

    if not project:
        conn.close()
        return None

    # --------------------------------------------------------
    # MEMORY
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            id,
            memory_type,
            content,
            asset_id,
            created_at,
            updated_at
        FROM project_memory
        WHERE project_id = ?
        ORDER BY memory_type, updated_at DESC
        """,
        (project_id,)
    )

    memories = cursor.fetchall()

    # --------------------------------------------------------
    # PANELS
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            id,
            file_path,
            created_at
        FROM panels
        WHERE project_id = ?
        ORDER BY created_at DESC
        """,
        (project_id,)
    )

    panels = cursor.fetchall()

    # --------------------------------------------------------
    # GENERATED REFERENCES
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            id,
            source_panel_id,
            file_path,
            prompt,
            created_at
        FROM generated_references
        WHERE project_id = ?
        ORDER BY created_at DESC
        """,
        (project_id,)
    )

    generated_references = cursor.fetchall()

    conn.close()

    return {
        "project": project,
        "memories": memories,
        "panels": panels,
        "generated_references": generated_references
    }