from tools.project_memory_tools import (
    save_project_memory,
    get_project_memory,
    search_project,
    get_project_context,
)


PROJECT_ID = 6


print("\n========== SAVE ==========")

print(
    save_project_memory(
        project_id=PROJECT_ID,
        memory_type="character",
        content="Kageyama is a setter."
    )
)


print("\n========== SAVE DUPLICATE ==========")

print(
    save_project_memory(
        project_id=PROJECT_ID,
        memory_type="character",
        content="Kageyama is a setter."
    )
)


print("\n========== GET MEMORY ==========")

print(
    get_project_memory(
        project_id=PROJECT_ID
    )
)


print("\n========== SEARCH ==========")

print(
    search_project(
        project_id=PROJECT_ID,
        query="Kageyama"
    )
)


print("\n========== CONTEXT ==========")

print(
    get_project_context(
        project_id=PROJECT_ID
    )
)