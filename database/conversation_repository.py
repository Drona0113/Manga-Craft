from database.database import get_connection


# ============================================================
# CREATE CONVERSATION
# ============================================================

def create_conversation(project_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO conversations (project_id)
        VALUES (?)
        """,
        (project_id,)
    )

    conn.commit()

    conversation_id = cursor.lastrowid

    conn.close()

    return conversation_id


# ============================================================
# GET PROJECT CONVERSATION
# ============================================================

def get_conversation(project_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, project_id, created_at, updated_at
        FROM conversations
        WHERE project_id = ?
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        (project_id,)
    )

    conversation = cursor.fetchone()

    conn.close()

    return conversation


# ============================================================
# UPDATE CONVERSATION TIMESTAMP
# ============================================================

def touch_conversation(conversation_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE conversations
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (conversation_id,)
    )

    conn.commit()

    conn.close()


# ============================================================
# SAVE MESSAGE
# ============================================================

def save_message(
    conversation_id,
    role,
    content
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO messages (
            conversation_id,
            role,
            content
        )
        VALUES (?, ?, ?)
        """,
        (
            conversation_id,
            role,
            content
        )
    )

    conn.commit()

    message_id = cursor.lastrowid

    conn.close()

    return message_id


# ============================================================
# GET MESSAGES
# ============================================================

def get_messages(conversation_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, conversation_id, role, content, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id ASC
        """,
        (conversation_id,)
    )

    messages = cursor.fetchall()

    conn.close()

    return messages