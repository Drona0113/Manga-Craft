from database.database import get_connection


# ============================================================
# CREATE PROJECT
# ============================================================

def create_project(name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO projects (name)
        VALUES (?)
        """,
        (name,)
    )

    conn.commit()

    project_id = cursor.lastrowid

    conn.close()

    return project_id


# ============================================================
# GET ALL PROJECTS
# ============================================================

def get_projects():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, created_at, updated_at, last_opened
        FROM projects
        ORDER BY updated_at DESC
        """
    )

    projects = cursor.fetchall()

    conn.close()

    return projects


# ============================================================
# GET SINGLE PROJECT
# ============================================================

def get_project(project_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, created_at, updated_at, last_opened
        FROM projects
        WHERE id = ?
        """,
        (project_id,)
    )

    project = cursor.fetchone()

    conn.close()

    return project


# ============================================================
# REMEMBER LAST OPENED PROJECT
# ============================================================

def remember_last_project(project_id):

    conn = get_connection()
    cursor = conn.cursor()

    # Mark every project as not last opened
    cursor.execute(
        """
        UPDATE projects
        SET last_opened = 0
        """
    )

    # Mark selected project as last opened
    cursor.execute(
        """
        UPDATE projects
        SET last_opened = 1
        WHERE id = ?
        """,
        (project_id,)
    )

    conn.commit()

    conn.close()

    print(
        f"💾 LAST OPENED PROJECT SAVED: {project_id}"
    )




# ============================================================
# GET LAST OPENED PROJECT
# ============================================================

def get_last_opened_project():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, created_at, updated_at, last_opened
        FROM projects
        WHERE last_opened = 1
        LIMIT 1
        """
    )

    project = cursor.fetchone()

    conn.close()

    return project


# ============================================================
# UPDATE PROJECT
# ============================================================

def update_project(project_id, name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE projects
        SET name = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (name, project_id)
    )

    conn.commit()

    conn.close()


# ============================================================
# DELETE PROJECT
# ============================================================

def delete_project(project_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM projects
        WHERE id = ?
        """,
        (project_id,)
    )

    conn.commit()

    conn.close()