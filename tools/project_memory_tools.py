from database.project_memory_repository import (
    save_project_memory as db_save_project_memory,
    get_project_memory as db_get_project_memory,
    search_project_memory as db_search_project_memory,
    get_project_context as db_get_project_context,
)


# ============================================================
# SAVE PROJECT MEMORY
# ============================================================

def save_project_memory(
    project_id: int,
    memory_type: str,
    content: str,
    asset_id: int | None = None,
) -> str:
    """
    Save a fact or decision to the current project memory.
    """

    if not content or not content.strip():
        return "Memory content cannot be empty."

    result = db_save_project_memory(
        project_id=project_id,
        memory_type=memory_type,
        content=content.strip(),
        asset_id=asset_id,
    )

    if result["status"] == "already_exists":
        return (
            f"Memory already exists for project {project_id}. "
            f"Memory ID: {result['id']}"
        )

    return (
        f"Memory saved successfully for project {project_id}. "
        f"Memory ID: {result['id']}"
    )


# ============================================================
# GET PROJECT MEMORY
# ============================================================

def get_project_memory(
    project_id: int,
    memory_type: str | None = None,
) -> str:
    """
    Retrieve memories stored for a project.
    """

    memories = db_get_project_memory(
        project_id=project_id,
        memory_type=memory_type,
    )

    if not memories:
        return f"No project memories found for project {project_id}."

    lines = []

    for memory in memories:
        lines.append(
            f"[{memory['memory_type']}] {memory['content']}"
        )

    return "\n".join(lines)


# ============================================================
# SEARCH PROJECT
# ============================================================

def search_project(
    project_id: int,
    query: str,
) -> str:
    """
    Search project memory for information relevant to a query.
    """

    if not query or not query.strip():
        return "Search query cannot be empty."

    results = db_search_project_memory(
        project_id=project_id,
        query=query.strip(),
    )

    if not results:
        return (
            f"No project information found matching "
            f"'{query}' for project {project_id}."
        )

    lines = []

    for result in results:
        lines.append(
            f"[{result['memory_type']}] {result['content']}"
        )

    return "\n".join(lines)


# ============================================================
# GET PROJECT CONTEXT
# ============================================================

def get_project_context(
    project_id: int,
) -> str:
    """
    Build a complete context summary for the current project.
    """

    context = db_get_project_context(
        project_id=project_id
    )

    if not context:
        return f"Project {project_id} was not found."

    project = context["project"]

    lines = [
        f"PROJECT: {project['name']}",
        "",
        "PROJECT MEMORY:",
    ]

    memories = context["memories"]

    if memories:
        for memory in memories:
            lines.append(
                f"- [{memory['memory_type']}] "
                f"{memory['content']}"
            )
    else:
        lines.append("- No project memory stored.")

    lines.append("")
    lines.append("PANELS:")

    panels = context["panels"]

    if panels:
        for panel in panels:
            lines.append(
                f"- Panel {panel['id']}: {panel['file_path']}"
            )
    else:
        lines.append("- No panels stored.")

    lines.append("")
    lines.append("GENERATED REFERENCES:")

    references = context["generated_references"]

    if references:
        for reference in references:
            lines.append(
                f"- Reference {reference['id']}: "
                f"{reference['file_path']}"
            )
    else:
        lines.append("- No generated references stored.")

    return "\n".join(lines)


# ============================================================
# TOOL DEFINITIONS
# ============================================================

SAVE_PROJECT_MEMORY_TOOL = {
    "type": "function",
    "function": {
        "name": "save_project_memory",
        "description": (
            "Save new or updated project information to persistent project memory. "
            "Use this when the user establishes, declares, adds, corrects, updates, "
            "or explicitly asks to remember project information. "
            "A declarative statement such as 'Kageyama fights with arrogance' "
            "is a save action even if the user does not say 'remember' or 'save'. "
            "Do not use retrieval tools for newly provided project facts."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "memory_type": {
                    "type": "string",
                    "enum": [
                        "character",
                        "story",
                        "relationship",
                        "design_decision",
                        "art_style",
                        "preference",
                        "panel",
                        "generated_reference",
                        "character_reference",
                        "other_asset",
                    ],
                    "description": (
                        "The category of information being saved."
                    ),
                },
                "content": {
                    "type": "string",
                    "description": (
                        "The concise fact or information that "
                        "should be remembered."
                    ),
                },
                "asset_id": {
                    "type": ["integer", "null"],
                    "description": (
                        "Optional ID of the related project asset."
                    ),
                },
            },
            "required": [
                "memory_type",
                "content",
            ],
        },
    },
}


GET_PROJECT_MEMORY_TOOL = {
    "type": "function",
    "function": {
        "name": "get_project_memory",
        "description": (
            "Retrieve persistent memories from the current manga "
            "project. Use this when you need established facts, "
            "creative decisions, or other information stored in "
            "project memory.Do not use this tool to save or update information"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "memory_type": {
                    "type": ["string", "null"],
                    "enum": [
                        "character",
                        "story",
                        "relationship",
                        "design_decision",
                        "art_style",
                        "preference",
                        "panel",
                        "generated_reference",
                        "character_reference",
                        "other_asset",
                    ],
                    "description": (
                        "Optional memory category to retrieve. "
                        "If omitted, retrieve all project memory."
                    ),
                },
            },
            "required": [],
        },
    },
}


SEARCH_PROJECT_TOOL = {
    "type": "function",
    "function": {
        "name": "search_project",
        "description": (
            "Search persistent project memory for a specific piece of information "
            "requested by the user. Use this for targeted questions about an "
            "established project fact. Do not use this for broad project overviews "
            "or for newly provided project information."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The information or topic to search for "
                        "within the current project."
                    ),
                },
            },
            "required": [
                "query",
            ],
        },
    },
}


GET_PROJECT_CONTEXT_TOOL = {
    "type": "function",
    "function": {
        "name": "get_project_context",
        "description": (
            "Get the complete current project context from the project "
            "database. MUST be used when the user asks for an overview, "
            "summary, status, or description of the current project, "
            "especially when they say 'using project data' or ask what "
            "is currently in the project. This tool returns the project "
            "name, all persistent project memories, stored panels, and "
            "generated references. Do not answer a broad project overview "
            "request from conversation history or from partial memory alone."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}

