# app.py

# 

import gradio as gr

from llm import craft_response
from tools.panel_tools import analyze_panel,composition_analysis,generate_reference
from database.project_repository import (
    create_project,
    get_projects,
    get_project,
    update_project,
    delete_project,
    remember_last_project,
    get_last_opened_project
)

from database.panel_repository import (
    get_latest_panel
)

from database.conversation_repository import (
    create_conversation,
    get_conversation,
    save_message,
    get_messages,
    touch_conversation
)

from database.generated_reference_repository import (
    create_generated_reference,
    get_generated_references,
    delete_generated_reference,
    get_generated_reference
)

def get_or_create_project_conversation(project_id):

    conversation = get_conversation(project_id)

    if conversation:
        return conversation["id"]

    return create_conversation(project_id)

from pathlib import Path
import shutil

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DATA_DIR = BASE_DIR / "data" / "projects"

PROJECT_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

from database.panel_repository import (
    save_panel,
    get_panels,
    get_latest_panel,
    delete_panel
)

def chat_response(message, history, panel_image, selected_panel, conversation_history,project_choice):

    print("\n========== CHAT RESPONSE ==========")
    print("MESSAGE:", message)
    print("CHATBOT HISTORY:", history)
    print("CONVERSATION HISTORY:", conversation_history)
    print("PANEL IMAGE:", panel_image)
    print("PROJECT CHOICE : ",project_choice)
    print("SELECTED PANEL:", selected_panel)
    print("===================================\n")

    history = history or []
    conversation_history = conversation_history or []
    #GET CURRENT PROJECT
    if not project_choice:

        gr.Warning(
            "Please select a project first."
        )

        return (
            history,
            conversation_history,
            None
        )

    project_id = int(
        project_choice.split("|")[0].strip()
    )

    print(" CURRENT PROJECT ID:", project_id)

    # --------------------------------------------------------
    # Get / create project conversation
    # --------------------------------------------------------

    conversation = get_conversation(project_id)

    if conversation:

        conversation_id = conversation["id"]

    else:

        conversation_id = create_conversation(
            project_id
        )

    print(
        "CONVERSATION ID:",
        conversation_id
    )


    conversation_id = get_or_create_project_conversation(
        project_id
    )

    print("CONVERSATION ID:", conversation_id)
    response,new_generation_request= craft_response(
        message,
        conversation_history,
        panel_image=panel_image,
        selected_image=selected_panel
    )

    user_content = []

    if selected_panel:
        user_content.append(
            {"path": selected_panel}
        )

    user_content.append(message)

    updated_history = conversation_history + [
        {
            "role": "user",
            "content": user_content
        },
        {
            "role": "assistant",
            "content": response
        }
    ]
    # ========================================================
    # SAVE CONVERSATION TO SQLITE
    # ========================================================
    save_message(
        conversation_id,
        "user",
        message
    )

    save_message(
        conversation_id,
        "assistant",
        response
    )

    touch_conversation(
        conversation_id
    )

    print(
        "✅ Conversation messages saved to SQLite"
    )
    print("\n========== UPDATED CONVERSATION HISTORY ==========")
    print(updated_history)
    print("==================================================\n")


    if new_generation_request:
        gr.Info(
            "🎨 Generation Request Ready\n\n"
            "Your reference request is ready. "
            "Click **Generate Reference** in the Panel Tools "
            "to generate the image.",
            duration=7
        )

    return updated_history, updated_history, new_generation_request



def analyze_panel_action(panel_image, history):
    history = history or []
    print("\n========== DIRECT BUTTON ==========")
    print("Panel:", panel_image)
    print("===================================\n")
    if not panel_image:
        return history + [
            {
                "role": "assistant",
                "content": "Please upload a manga panel first."
            }
        ]

    # Explicitly execute the panel-analysis tool
    result = analyze_panel(panel_image)
    print("DIRECT TOOL RESULT:")
    print(result)
    print("===================================\n")
    return history + [
        {
            "role": "user",
            "content": [
                {"path": panel_image},
                "Analyze this panel"
            ]
        },
        {
            "role": "assistant",
            "content": result
        }
    ]


def composition_analysis_action(panel_image, history):
    history = history or []
    print("\n========== DIRECT BUTTON ==========")
    print("Panel:", panel_image)
    print("===================================\n")
    if not panel_image:
        return history + [
            {
                "role": "assistant",
                "content": "Please upload a manga panel first."
            }
        ]

    result = composition_analysis(panel_image)
    print("DIRECT TOOL RESULT:")
    print(result)
    print("===================================\n")

    return history + [
        {
            "role": "user",
            "content": [
                {"path": panel_image},
                "Analyze the composition of this panel"
            ]
        },
        {
            "role": "assistant",
            "content": result
        }
    ]

def use_panel(panel_image):

    if not panel_image:
        gr.Warning("Please upload a panel first.")
        return None, "**Selected Panel:** None"

    filename = panel_image.split("\\")[-1]

    return (
        panel_image,
        f"**Selected Panel:** `{filename}`"
    )


def select_generated_reference(
    evt: gr.SelectData,
    selected_indices
):
    """
    Toggle generated references using their Gallery index.

    We intentionally use the index instead of the file path
    because multiple generated references may temporarily
    point to the same image file during testing.
    """

    selected_indices = list(
        selected_indices or []
    )

    print("\n========== GENERATED REFERENCE SELECTED ==========")
    print("Selected value:", evt.value)
    print("Selected index:", evt.index)

    # ----------------------------------------------------
    # Gradio can return an integer index or sometimes
    # a tuple/list depending on the component state.
    # ----------------------------------------------------

    index = evt.index

    if isinstance(index, (list, tuple)):
        index = index[0]

    if index is None:
        return (
            selected_indices,
            f"✓ {len(selected_indices)} selected"
        )

    # ----------------------------------------------------
    # Toggle by INDEX
    # ----------------------------------------------------

    if index in selected_indices:

        selected_indices.remove(index)

        print("❌ REMOVED INDEX:", index)

    else:

        selected_indices.append(index)

        print("✅ ADDED INDEX:", index)

    # ----------------------------------------------------
    # Debug
    # ----------------------------------------------------

    print("\nCURRENT SELECTED REFERENCE INDICES:")

    for selected_index in selected_indices:
        print(" -", selected_index)

    print(
        "TOTAL SELECTED:",
        len(selected_indices)
    )

    print("==================================================\n")

    return (
        selected_indices,
        f"✓ {len(selected_indices)} selected"
    )

def delete_generated_reference_action(
    project_choice,
    evt: gr.EventData,
    selected_indices
):

    print("\n========== DELETE GENERATED REFERENCE ==========")

    if not project_choice:
        print("❌ No project selected.")
        return [], [], "0 selected"

    if evt is None or evt.file is None:
        print("❌ No deleted file information.")
        return gr.update(), selected_indices, f"{len(selected_indices or [])} selected"

    deleted_path = evt.file["path"]

    print("DELETED FILE PATH:", deleted_path)

    project_id = int(
        project_choice.split("|")[0].strip()
    )

    print("PROJECT ID:", project_id)

    # ----------------------------------------------------
    # Find database record using the generated image path
    # ----------------------------------------------------

    references = get_generated_references(
        project_id
    )

    deleted_reference = None

    for reference in references:

        if Path(reference["file_path"]).resolve() == Path(deleted_path).resolve():

            deleted_reference = reference
            break

    # ----------------------------------------------------
    # Delete database record
    # ----------------------------------------------------

    if deleted_reference:

        reference_id = deleted_reference["id"]

        print(
            "DELETING DATABASE REFERENCE:",
            reference_id
        )

        delete_generated_reference(
            reference_id
        )

    else:

        print(
            "⚠️ No database record found for:",
            deleted_path
        )

    # ----------------------------------------------------
    # Delete actual generated image
    # ----------------------------------------------------

    file_path = Path(deleted_path)

    if file_path.exists():

        try:

            file_path.unlink()

            print(
                "🗑 IMAGE FILE DELETED:",
                file_path
            )

        except Exception as e:

            print(
                "❌ FILE DELETE ERROR:",
                e
            )

    else:

        print(
            "⚠️ Image file already missing:",
            file_path
        )

    # ----------------------------------------------------
    # Remove deleted index from selection state
    # ----------------------------------------------------

    selected_indices = list(
        selected_indices or []
    )

    # We don't know the gallery index directly from
    # DeletedFileData, so reload selection safely.
    #
    # Existing selected indices are cleared because
    # gallery ordering may have changed after deletion.

    selected_indices = []

    # ----------------------------------------------------
    # Reload remaining references
    # ----------------------------------------------------

    remaining_references = get_generated_references(
        project_id
    )

    generated_references = [
        reference["file_path"]
        for reference in remaining_references
    ]

    print(
        "REMAINING REFERENCES:",
        len(generated_references)
    )

    print("===============================================\n")

    return (
        generated_references,
        selected_indices,
        "0 selected"
    )



def use_generated(
    selected_indices,
    generated_references
):

    selected_indices = list(
        selected_indices or []
    )

    print("\n========== USE GENERATED ==========")

    if not selected_indices:

        print("❌ No generated references selected.")
        print("===================================\n")

        gr.Warning(
            "Please select at least one generated reference."
        )

        return (
            None,
            "**Selected Panel:** None"
        )

    print("SELECTED INDICES:")

    for index in selected_indices:
        print(" -", index)

    # ----------------------------------------------------
    # Resolve indices → actual image paths
    # ----------------------------------------------------

    selected_paths = []

    for index in selected_indices:

        if index >= len(generated_references):
            continue

        item = generated_references[index]

        # Gallery item may be a dictionary
        if isinstance(item, dict):

            image_data = item.get("image")

            if isinstance(image_data, dict):

                path = image_data.get("path")

            else:

                path = image_data

        else:

            path = item

        if path:
            selected_paths.append(path)

    # ----------------------------------------------------
    # Nothing resolved
    # ----------------------------------------------------

    if not selected_paths:

        gr.Warning(
            "Unable to resolve the selected references."
        )

        return (
            None,
            "**Selected Panel:** None"
        )

    # ----------------------------------------------------
    # Debug
    # ----------------------------------------------------

    print("\nRESOLVED SELECTED REFERENCES:")

    for index, path in zip(
        selected_indices,
        selected_paths
    ):
        print(
            f" {index} → {path}"
        )

    print(
        "TOTAL:",
        len(selected_paths)
    )

    print("===================================\n")

    # ----------------------------------------------------
    # TEMPORARY BEHAVIOR
    #
    # Until multi-reference generation is implemented,
    # use the first selected image as the active panel.
    #
    # ALL selected references remain represented by
    # selected_indices state.
    # ----------------------------------------------------

    primary_image = selected_paths[0]

    filename = Path(primary_image).name

    return (
        primary_image,
        f"**Selected Panel:** `{filename}`  \n"
        f"**References:** `{len(selected_paths)}` selected"
    )



def clear_panel():
    return None, "**Selected Panel:** None"

def update_panel_image_text(panel_image):
    if not panel_image:
        return "**Panel Image:** None"

    filename = panel_image.split("\\")[-1]

    return f"**Panel Image:** `{filename}`"

# def generate_reference_action(selected_panel, history):

#     print("\n========== GENERATE REFERENCE ==========")
#     print("Selected Panel:", selected_panel)

#     print("HISTORY VALUE:")
#     print(history)

#     print("HISTORY TYPE:")
#     print(type(history))

#     if history:
#         print("HISTORY LENGTH:")
#         print(len(history))

#     print("========================================\n")
#     # --------------------------------------------------------
#     # Check selected panel
#     # --------------------------------------------------------

#     if not selected_panel:
#         print("❌ No selected panel")
#         return None

#     # --------------------------------------------------------
#     # Check history
#     # --------------------------------------------------------

#     if not history:
#         print("❌ No chatbot history")
#         return None

#     # --------------------------------------------------------
#     # Find the latest textual user request
#     # --------------------------------------------------------

#     latest_user_message = None

#     for chat_message in reversed(history):

#         if chat_message["role"] != "user":
#             continue

#         content = chat_message.get("content")

#         # ----------------------------------------------------
#         # Normal text message
#         # ----------------------------------------------------

#         if isinstance(content, str):

#             # Ignore Gradio file URLs
#             if "/gradio_api/file=" not in content:
#                 latest_user_message = content
#                 break

#         # ----------------------------------------------------
#         # Message containing image + text
#         # ----------------------------------------------------

#         elif isinstance(content, list):

#             text_parts = []

#             for item in content:

#                 # Plain text
#                 if isinstance(item, str):

#                     if "/gradio_api/file=" not in item:
#                         text_parts.append(item)

#                 # Image/file dictionary
#                 elif isinstance(item, dict):

#                     # Ignore image information
#                     if "path" in item:
#                         continue

#                     if "url" in item:
#                         continue

#             if text_parts:

#                 latest_user_message = " ".join(text_parts)
#                 break

#     # --------------------------------------------------------
#     # Debug extracted request
#     # --------------------------------------------------------

#     print("\nLATEST USER REQUEST:")
#     print(latest_user_message)

#     if not latest_user_message:
#         print("❌ No user request found")
#         return None

#     # --------------------------------------------------------
#     # Build image-generation prompt
#     # --------------------------------------------------------

#     prompt = f"""
# Create a manga drawing reference based on the selected panel.

# User's request:
# {latest_user_message}

# Preserve the important visual relationships from the selected panel,
# including the character pose, composition, perspective, character
# placement, and major visual elements unless the user's request
# explicitly asks to change them.

# Do not introduce unrelated characters or major elements.

# Generate the reference according to the user's request.
# """

#     # --------------------------------------------------------
#     # Debug generation prompt
#     # --------------------------------------------------------

#     print("\nREFERENCE PROMPT:")
#     print(prompt)

#     # --------------------------------------------------------
#     # Generate reference image
#     # --------------------------------------------------------

#     result = generate_reference(
#         selected_panel,
#         prompt
#     )

#     print("Generated:", result)
#     print("========================================\n")

#     # --------------------------------------------------------
#     # Return generated image path
#     # --------------------------------------------------------

#     return result

def test_generate_reference_action(
    project_choice,
    selected_panel,
    generation_request
):

    print("\n========== TEST GENERATE REFERENCE ==========")

    if not project_choice:
        gr.Warning("Please select a project first.")
        return []

    if not selected_panel:
        gr.Warning("Please click 📎 Use Panel first.")
        return []

    project_id = int(
        project_choice.split("|")[0].strip()
    )

    # --------------------------------------------------------
    # TEMPORARY TEST
    # Use the selected panel as a fake generated image.
    # --------------------------------------------------------

    result = selected_panel

    reference_id = create_generated_reference(
        project_id=project_id,
        file_path=result,
        prompt=generation_request or "Test reference"
    )

    print("TEST REFERENCE ID:", reference_id)

    # --------------------------------------------------------
    # Reload references from database
    # --------------------------------------------------------

    references = get_generated_references(
        project_id
    )

    return [
        reference["file_path"]
        for reference in references
    ]

def generate_reference_action(
    project_choice,
    selected_panel,
    generation_request
):

    print("\n========== GENERATE REFERENCE ==========")
    print("Project:", project_choice)
    print("Selected Panel:", selected_panel)
    print("Generation Request:", generation_request)
    print("========================================\n")

    # --------------------------------------------------------
    # Check project
    # --------------------------------------------------------

    if not project_choice:

        gr.Warning(
            "Please select a project first."
        )

        return None

    # --------------------------------------------------------
    # Check selected panel
    # --------------------------------------------------------

    if not selected_panel:

        gr.Warning(
            "Please click 📎 Use Panel before generating a reference."
        )

        return None

    # --------------------------------------------------------
    # Check generation request
    # --------------------------------------------------------

    if not generation_request:

        gr.Warning(
            "Please ask the chatbot for a reference generation "
            "request first."
        )

        return None

    # --------------------------------------------------------
    # Extract project ID
    # --------------------------------------------------------

    project_id = int(
        project_choice.split("|")[0].strip()
    )

    # --------------------------------------------------------
    # Generate reference
    # --------------------------------------------------------

    result = generate_reference(
        selected_panel,
        generation_request
    )

    print("Generated:", result)

    # --------------------------------------------------------
    # Save generated reference
    # --------------------------------------------------------

    reference_id = create_generated_reference(
        project_id=project_id,
        file_path=result,
        prompt=generation_request
    )

    print("REFERENCE ID:", reference_id)

    return result


# ============================================================
# PROJECT MANAGEMENT
# ============================================================

def load_projects():

    projects = get_projects()

    print("\n========== LOAD PROJECTS ==========")

    for project in projects:
        print(
            "PROJECT:",
            project["id"],
            "|",
            project["name"]
        )

    choices = [
        f"{project['id']} | {project['name']}"
        for project in projects
    ]

    print("DROPDOWN CHOICES:", choices)
    print("===================================\n")

    return choices

def get_default_project():

    print("\n========== GET DEFAULT PROJECT ==========")

    # --------------------------------------------------------
    # Try to restore the last opened project
    # --------------------------------------------------------

    project = get_last_opened_project()

    if project:

        project_choice = (
            f"{project['id']} | {project['name']}"
        )

        print(
            "✅ RESTORING LAST PROJECT:",
            project_choice
        )

        return project_choice

    # --------------------------------------------------------
    # No previous project
    # Use first project
    # --------------------------------------------------------

    projects = get_projects()

    if not projects:

        print("⚠️ NO PROJECTS FOUND")

        return None

    project = projects[0]

    project_choice = (
        f"{project['id']} | {project['name']}"
    )

    print(
        "⚠️ NO LAST PROJECT — USING:",
        project_choice
    )

    # Remember it
    remember_last_project(
        project["id"]
    )

    return project_choice

def create_project_action(project_name):

    if not project_name or not project_name.strip():

        return (
            gr.update(),
            None,
            "⚠️ Please enter a project name."
        )

    project_name = project_name.strip()

    project_id = create_project(project_name)

    # Remember newly created project
    remember_last_project(project_id)

    projects = load_projects()

    return (
        gr.update(
            choices=projects,
            value=f"{project_id} | {project_name}"
        ),
        project_id,
        f"✅ Project **{project_name}** created."
    )


def delete_project_action(project_choice):

    if not project_choice:

        return (
            gr.update(),
            "⚠️ Please select a project first."
        )

    project_id = int(
        project_choice.split("|")[0].strip()
    )

    delete_project(project_id)

    projects = load_projects()

    return (
        gr.update(
            choices=projects,
            value=None
        ),
        "✅ Project deleted."
    )


def rename_project_action(
    project_choice,
    new_name
):

    if not project_choice:

        return (
            gr.update(),
            "⚠️ Please select a project first."
        )

    if not new_name or not new_name.strip():

        return (
            gr.update(),
            "⚠️ Please enter a new project name."
        )

    project_id = int(
        project_choice.split("|")[0].strip()
    )

    update_project(
        project_id,
        new_name.strip()
    )

    projects = load_projects()

    return (
        gr.update(
            choices=projects,
            value=f"{project_id} | {new_name.strip()}"
        ),
        f"✅ Project renamed to **{new_name.strip()}**."
    )


def remember_project_action(project_choice):

    if not project_choice:
        return

    project_id = int(
        project_choice.split("|")[0].strip()
    )

    print("\n========== PROJECT SELECTED ==========")
    print("PROJECT CHOICE:", project_choice)

    remember_last_project(project_id)

    print("======================================\n")


# ============================================================
# LOAD PROJECT
# ============================================================

def load_project_action(project_choice):

    print("\n========== PROJECT LOADED ==========")
    print("PROJECT CHOICE:", project_choice)

    # --------------------------------------------------------
    # No project selected
    # --------------------------------------------------------

    if not project_choice:

        return (
            None,                  # panel_image
            "**Panel Image:** None",
            None,                  # selected_panel
            "**Selected Panel:** None",
            [],                    # chatbot
            [],                    # conversation_history
            None,                   # generation_request
            [],
            []
        )

    # --------------------------------------------------------
    # Extract project ID
    # --------------------------------------------------------

    project_id = int(
        project_choice.split("|")[0].strip()
    )

    project = get_project(project_id)

    if not project:

        print("❌ Project not found.")

        return (
            None,
            "**Panel Image:** None",
            None,
            "**Selected Panel:** None",
            [],
            [],
            None,
            [],
            []
        )

    print("PROJECT ID:", project["id"])
    print("PROJECT NAME:", project["name"])

    # ========================================================
    # LOAD LATEST PANEL
    # ========================================================

    panel = get_latest_panel(project_id)

    panel_path = None

    if panel:

        panel_path = panel["file_path"]

        print("PANEL LOADED:", panel_path)

    else:

        print("NO PANEL FOUND")

    # ========================================================
    # LOAD / CREATE CONVERSATION
    # ========================================================

    conversation = get_conversation(project_id)

    if conversation:

        conversation_id = conversation["id"]

    else:

        conversation_id = create_conversation(project_id)

    print("CONVERSATION ID:", conversation_id)

    # ========================================================
    # LOAD MESSAGES
    # ========================================================

    messages = get_messages(conversation_id)

    print("MESSAGES:", len(messages))

    # ========================================================
    # LOAD GENERATED REFERENCES
    # ========================================================

    references = get_generated_references(project_id)

    generated_references = []
    generated_reference_metadata = []

    for reference in references:

        generated_references.append(
            reference["file_path"]
        )

        generated_reference_metadata.append(
            {
                "id": reference["id"],
                "file_path": reference["file_path"],
                "prompt": reference["prompt"]
            }
        )

    print(
        "GENERATED REFERENCES:",
        len(generated_references)
    )

    # ========================================================
    # CONVERT DATABASE MESSAGES → GRADIO HISTORY
    # ========================================================

    history = []

    for msg in messages:

        history.append(
            {
                "role": msg["role"],
                "content": msg["content"]
            }
        )

    

    # ========================================================
    # PANEL TEXT
    # ========================================================

    if panel_path:

        filename = panel_path.split("\\")[-1]

        panel_text = (
            f"**Panel Image:** `{filename}`"
        )

        selected_text = (
            f"**Selected Panel:** `{filename}`"
        )

    else:

        panel_text = "**Panel Image:** None"
        selected_text = "**Selected Panel:** None"

    # ========================================================
    # RETURN
    # ========================================================

    return (
        panel_path,
        panel_text,
        panel_path,
        selected_text,
        history,
        history,
        None,
        generated_references,
        generated_reference_metadata
    )



from database.database import init_db

init_db()




def save_uploaded_panel(project_id, panel_image):

    if not project_id:
        gr.Warning(
            "Please select a project before uploading a panel."
        )
        return None

    if not panel_image:
        return None

    project_dir = (
        PROJECT_DATA_DIR / str(project_id) / "panels"
    )

    project_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    source = Path(panel_image)

    destination = project_dir / source.name

    shutil.copy2(
        source,
        destination
    )

    panel_id = save_panel(
        project_id,
        str(destination)
    )

    print("\n========== PANEL SAVED ==========")
    print("PANEL ID:", panel_id)
    print("PROJECT ID:", project_id)
    print("SOURCE:", source)
    print("DESTINATION:", destination)
    print("=================================\n")

    return str(destination)


def save_uploaded_panel_action(project_choice, panel_image):

    if not project_choice:
        gr.Warning(
            "Please select a project before uploading a panel."
        )
        return None

    project_id = int(
        project_choice.split("|")[0].strip()
    )

    return save_uploaded_panel(
        project_id,
        panel_image
    )


# ============================================================
# MANGACRAFT UI
# ============================================================

CUSTOM_CSS = """
/* ============================================================
   GLOBAL
   ============================================================ */

body {
    background: #0f1117 !important;
    color: #e5e7eb !important;
}

.gradio-container {
    max-width: 1600px !important;
    margin: 0 auto !important;
    padding: 0 !important;
    background: #0f1117 !important;
}

/* Remove default Gradio white backgrounds */

.gradio-container,
.gradio-container > div,
.block,
.block.gradio-row,
.block.gradio-column {
    background: transparent !important;
}


/* ============================================================
   HEADER
   ============================================================ */

.mc-header {
    height: 64px;

    display: flex;
    align-items: center;
    justify-content: space-between;

    padding: 0 24px !important;

    background: #151821 !important;

    border-bottom: 1px solid #292d38;
}

.mc-logo {
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: #f9fafb;
}

.mc-project-name {
    font-size: 14px;
    font-weight: 500;
    color: #9ca3af;
}


/* ============================================================
   MAIN LAYOUT
   ============================================================ */

.mc-main {
    gap: 0 !important;

    align-items: stretch !important;

    min-height: calc(100vh - 64px);

    background: #0f1117 !important;
}


/* ============================================================
   PROJECTS
   ============================================================ */

.mc-projects {
    background: #151821 !important;

    border-right: 1px solid #292d38;

    padding: 22px 18px !important;

    min-height: calc(100vh - 64px);

    height: auto !important;

    box-sizing: border-box;
}


/* ============================================================
   WORKSPACE
   ============================================================ */

.mc-workspace {
    background: #10131a !important;

    padding: 24px 28px !important;

    min-height: calc(100vh - 64px);

    height: auto !important;

    box-sizing: border-box;
}


/* ============================================================
   AI ASSISTANT
   ============================================================ */

.mc-assistant {
    background: #151821 !important;

    border-left: 1px solid #292d38;

    padding: 22px 18px !important;

    min-height: calc(100vh - 64px);

    height: auto !important;

    box-sizing: border-box;
}


/* ============================================================
   SECTION HEADERS
   ============================================================ */

.mc-section-title {
    font-size: 14px;

    font-weight: 700;

    letter-spacing: 0.5px;

    color: #f3f4f6;

    margin-bottom: 4px;
}

.mc-section-subtitle {
    font-size: 12px;

    color: #6b7280;

    margin-bottom: 16px;
}


/* ============================================================
   PROJECT AREA
   ============================================================ */

.mc-project-list {
    margin-top: 8px;
}


/* Project dropdown */

.mc-projects .gradio-dropdown,
.mc-projects .gradio-textbox {
    background: #1b1f29 !important;

    border: 1px solid #2b303c !important;

    color: #e5e7eb !important;

    border-radius: 8px !important;
}


/* ============================================================
   PROJECT BUTTONS
   ============================================================ */

.mc-project-actions {
    margin-top: 12px;
}

.mc-project-actions button {
    min-height: 38px !important;
}

.mc-project-status {
    font-size: 12px !important;
    color: #9ca3af !important;
}


/* ============================================================
   WORKSPACE PANEL
   ============================================================ */

.mc-panel-card {
    border: 1px solid #292d38;

    border-radius: 12px;

    background: #171a22 !important;

    padding: 14px;

    margin-top: 12px;

    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
}


/* Panel image */

.mc-panel-image {
    background: #0b0d12 !important;

    border-radius: 8px;
}

.mc-panel-image img {
    border-radius: 8px;

    object-fit: contain !important;
}


/* Panel information */

.mc-panel-info {
    font-size: 12px;

    color: #9ca3af;

    margin-top: 6px;
}

.mc-selected-panel {
    font-size: 12px;

    color: #9ca3af;

    margin-top: 4px;
}


/* ============================================================
   PANEL ACTIONS
   ============================================================ */

.mc-panel-actions {
    margin-top: 10px;
}

.mc-panel-actions button {
    min-height: 40px !important;
}


/* ============================================================
   PANEL TOOLS
   ============================================================ */

.mc-panel-tools-title {
    font-size: 13px;

    font-weight: 700;

    color: #d1d5db;

    margin-top: 20px;

    margin-bottom: 8px;
}

.mc-tool-row {
    gap: 8px !important;
}

.mc-tool-row button {
    min-height: 40px !important;
}


/* ============================================================
   GENERATED REFERENCES HEADER
   ============================================================ */

.mc-generated-header {
    align-items: center !important;
    justify-content: space-between !important;
    margin-bottom: 8px;
}

.mc-generated-title {
    margin: 0 !important;
}

.mc-selected-count {
    font-size: 12px !important;
    color: #9ca3af !important;
    text-align: right;
    margin: 0 !important;
}


/* ============================================================
   AI CHATBOT
   ============================================================ */

.mc-chatbot {
    border: 1px solid #292d38 !important;

    border-radius: 12px !important;

    background: #10131a !important;

    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}


/* ============================================================
   CHAT INPUT
   ============================================================ */

.mc-chat-input {
    margin-top: 10px;
}

.mc-chat-input textarea {
    border-radius: 10px !important;

    background: #1b1f29 !important;

    border: 1px solid #2b303c !important;

    color: #e5e7eb !important;
}


/* ============================================================
   GENERAL TEXT INPUTS
   ============================================================ */

input,
textarea {
    background: #1b1f29 !important;

    color: #e5e7eb !important;

    border-color: #2b303c !important;
}

input::placeholder,
textarea::placeholder {
    color: #6b7280 !important;
}


/* ============================================================
   BUTTONS
   ============================================================ */

button {
    border-radius: 8px !important;
}

.mc-primary-btn {
    min-height: 40px !important;
}

.mc-secondary-btn {
    min-height: 40px !important;
}


/* ============================================================
   MARKDOWN
   ============================================================ */

.mc-projects h3,
.mc-workspace h3,
.mc-assistant h3 {
    color: #d1d5db !important;
}

.mc-projects p,
.mc-workspace p,
.mc-assistant p {
    color: #9ca3af;
}


/* ============================================================
   REMOVE EXCESS SPACING
   ============================================================ */

.mc-tight {
    margin: 0 !important;

    padding: 0 !important;
}

.mc-main {
    display: flex !important;
    flex-wrap: nowrap !important;
    align-items: stretch !important;
    gap: 0 !important;
    min-height: calc(100vh - 64px);
    width: 100% !important;
}


"""



with gr.Blocks(
    title="MangaCraft",
) as demo:

    # ========================================================
    # HEADER
    # ========================================================

    with gr.Row(elem_classes="mc-header",equal_height=True):

        gr.HTML(
            """
            <div class="mc-logo">
                ✦ MangaCraft
            </div>
            """
        )

        gr.HTML(
            """
            <div class="mc-project-name">
                AI Manga Workspace
            </div>
            """
        )

    # ========================================================
    # MAIN APPLICATION
    # ========================================================

    with gr.Row(
        elem_classes="mc-main"
    ):

        # ====================================================
        # LEFT — PROJECTS
        # ====================================================

        with gr.Column(
            scale=2,
            min_width=0,
            elem_classes="mc-projects"
        ):

            gr.HTML(
                """
                <div class="mc-section-title">
                    PROJECTS
                </div>
                <div class="mc-section-subtitle">
                    Your manga projects
                </div>
                """
            )

            project_dropdown = gr.Dropdown(
                label="Current Project",
                choices=load_projects(),
                value=get_default_project(),
                interactive=True,
                elem_classes="mc-project-list"
            )

            # ------------------------------------------------
            # NEW PROJECT
            # ------------------------------------------------

            gr.Markdown(
                "### New Project",
                elem_classes="mc-tight"
            )

            new_project_name = gr.Textbox(
                placeholder="Project name...",
                label=""
            )

            create_project_btn = gr.Button(
                "＋ New Project",
                variant="primary",
                elem_classes="mc-primary-btn"
            )

            # ------------------------------------------------
            # PROJECT MANAGEMENT
            # ------------------------------------------------

            gr.Markdown(
                "### Manage Project",
                elem_classes="mc-tight"
            )

            rename_project_name = gr.Textbox(
                placeholder="New project name...",
                label=""
            )

            with gr.Row():

                rename_project_btn = gr.Button(
                    "Rename",
                    elem_classes="mc-secondary-btn"
                )

                delete_project_btn = gr.Button(
                    "🗑 Delete",
                    elem_classes="mc-secondary-btn"
                )

            project_status = gr.Markdown(
                "",
                elem_classes="mc-project-status"
            )

        # ====================================================
        # CENTER — MANGA WORKSPACE
        # ====================================================

        with gr.Column(
            scale=5,
            min_width=0,
            elem_classes="mc-workspace"
        ):

            gr.HTML(
                """
                <div class="mc-section-title">
                    MANGA WORKSPACE
                </div>
                <div class="mc-section-subtitle">
                    Work with your manga panel
                </div>
                """
            )

            # ------------------------------------------------
            # PANEL
            # ------------------------------------------------

            with gr.Group(
                elem_classes="mc-panel-card"
            ):

                panel_image = gr.Image(
                    label="Panel",
                    type="filepath",
                    height=430,
                    elem_classes="mc-panel-image"
                )

                panel_image_text = gr.Markdown(
                    "**Panel Image:** None",
                    elem_classes="mc-panel-info"
                )

                selected_panel = gr.State(
                    value=None
                )

                generation_request = gr.State(
                    value=None
                )

                selected_generated_references = gr.State(
                    value=[]
                )
                generated_reference_metadata = gr.State(
                    value=[]
                )

                conversation_history = gr.State(
                    value=[]
                )

                current_project_id = gr.State(
                    value=None
                )

                

                selected_panel_text = gr.Markdown(
                    "**Selected Panel:** None",
                    elem_classes="mc-selected-panel"
                )

                # --------------------------------------------
                # PANEL ACTIONS
                # --------------------------------------------

                with gr.Row(
                    elem_classes="mc-panel-actions"
                ):

                    use_panel_btn = gr.Button(
                        "📎 Use Panel",
                        variant="primary"
                    )

                    clear_panel_btn = gr.Button(
                        "× Clear"
                    )

            # ------------------------------------------------
            # PANEL EVENTS
            # ------------------------------------------------

            panel_image.change(
                fn=update_panel_image_text,
                inputs=panel_image,
                outputs=panel_image_text
            )

            panel_image.upload(
                fn=save_uploaded_panel_action,
                inputs=[
                    project_dropdown,
                    panel_image
                ],
                outputs=panel_image
            )
            use_panel_btn.click(
                fn=use_panel,
                inputs=panel_image,
                outputs=[
                    selected_panel,
                    selected_panel_text
                ]
            )

            clear_panel_btn.click(
                fn=clear_panel,
                inputs=None,
                outputs=[
                    selected_panel,
                    selected_panel_text
                ]
            )

            # ------------------------------------------------
            # PANEL TOOLS
            # ------------------------------------------------

            gr.HTML(
                """
                <div class="mc-panel-tools-title">
                    PANEL TOOLS
                </div>
                """
            )

            with gr.Row(
                elem_classes="mc-tool-row"
            ):

                analyze_btn = gr.Button(
                    "🔍 Analyze Panel",
                    elem_classes="mc-secondary-btn"
                )

                composition_btn = gr.Button(
                    "📐 Composition",
                    elem_classes="mc-secondary-btn"
                )

            generate_btn = gr.Button(
                "🎨 Generate Reference",
                variant="primary",
                elem_classes="mc-primary-btn"
            )

            # ------------------------------------------------
            # GENERATED REFERENCES
            # ------------------------------------------------

            with gr.Column(
                scale=5,
                min_width=0,
                elem_classes="mc-generated"
            ):

                with gr.Row(elem_classes="mc-generated-header"):

                    gr.Markdown(
                        "### Generated References",
                        elem_classes="mc-generated-title"
                    )

                    selected_reference_count = gr.Markdown(
                        "0 selected",
                        elem_classes="mc-selected-count"
                    )

                generated_gallery = gr.Gallery(
                    label="",
                    columns=3,
                    rows=1,
                    height=220,
                    object_fit="contain",
                    allow_preview=True,
                    interactive=True
                )

                generated_gallery.select(
                    fn=select_generated_reference,
                    inputs=selected_generated_references,
                    outputs=[
                        selected_generated_references,
                        selected_reference_count
                    ]
                )
                generated_gallery.delete(
                    fn=delete_generated_reference_action,
                    inputs=[
                        project_dropdown,
                        selected_generated_references
                    ],
                    outputs=[
                        generated_gallery,
                        selected_generated_references,
                        selected_reference_count
                    ]
                )

                use_generated_btn = gr.Button(
                    "📎 Use Generated"
                )
                
        # ====================================================
        # RIGHT — AI ASSISTANT
        # ====================================================

        with gr.Column(
            scale=3,
            min_width=0,
            elem_classes="mc-assistant"
        ):

            gr.HTML(
                """
                <div class="mc-section-title">
                    AI ASSISTANT
                </div>
                <div class="mc-section-subtitle">
                    Your manga co-pilot
                </div>
                """
            )

            chatbot = gr.Chatbot(
                label="Conversation",
                height=650,
                elem_classes="mc-chatbot"
            )

            # ------------------------------------------------
            # CHAT INPUT
            # ------------------------------------------------

            with gr.Row(
                elem_classes="mc-chat-input"
            ):

                message = gr.Textbox(
                    placeholder="Ask MangaCraft...",
                    label="",
                    scale=5,
                    lines=2
                )

                send_btn = gr.Button(
                    "➤",
                    scale=1,
                    min_width=55,
                    variant="primary"
                )

            # =================================================
            # CHAT EVENTS
            # =================================================

            send_event = send_btn.click(
                fn=chat_response,
                inputs=[
                    message,
                    chatbot,
                    panel_image,
                    selected_panel,
                    conversation_history,
                    project_dropdown
                ],
                outputs=[
                    chatbot,
                    conversation_history,
                    generation_request
                ]
            )

            enter_event = message.submit(
                fn=chat_response,
                inputs=[
                    message,
                    chatbot,
                    panel_image,
                    selected_panel,
                    conversation_history,
                    project_dropdown
                ],
                outputs=[
                    chatbot,
                    conversation_history,
                    generation_request
                ]
            )

            send_event.then(
                fn=lambda: "",
                inputs=None,
                outputs=message
            )

            enter_event.then(
                fn=lambda: "",
                inputs=None,
                outputs=message
            )

            # =================================================
            # DIRECT PANEL TOOLS
            # =================================================

            analyze_btn.click(
                fn=analyze_panel_action,
                inputs=[
                    panel_image,
                    chatbot
                ],
                outputs=chatbot
            )

            composition_btn.click(
                fn=composition_analysis_action,
                inputs=[
                    panel_image,
                    chatbot
                ],
                outputs=chatbot
            )

            # =================================================
            # GENERATE REFERENCE
            # =================================================

            generate_btn.click(
                fn=test_generate_reference_action,
                inputs=[
                    project_dropdown,
                    selected_panel,
                    generation_request
                ],
                outputs=generated_gallery
            )

            

            # =================================================
            # USE GENERATED REFERENCE
            # =================================================

            use_generated_btn.click(
                fn=use_generated,
                inputs=[
                    selected_generated_references,
                    generated_gallery
                ],
                outputs=[
                    selected_panel,
                    selected_panel_text
                ]
            )
    


            # =================================================
            # PROJECT MANAGEMENT EVENTS
            # =================================================

            create_project_btn.click(
                fn=create_project_action,
                inputs=new_project_name,
                outputs=[
                    project_dropdown,
                    current_project_id,
                    project_status
                ]
            )

            rename_project_btn.click(
                fn=rename_project_action,
                inputs=[
                    project_dropdown,
                    rename_project_name
                ],
                outputs=[
                    project_dropdown,
                    project_status
                ]
            )

            delete_project_btn.click(
                fn=delete_project_action,
                inputs=project_dropdown,
                outputs=[
                    project_dropdown,
                    project_status
                ]
            )

            # =================================================
            # LOAD PROJECT
            # =================================================

            project_dropdown.change(
                fn=remember_project_action,
                inputs=project_dropdown,
                outputs=None
            ).then(
                fn=load_project_action,
                inputs=project_dropdown,
                outputs=[
                    panel_image,
                    panel_image_text,
                    selected_panel,
                    selected_panel_text,
                    chatbot,
                    conversation_history,
                    generation_request,
                    generated_gallery,
                    generated_reference_metadata
                ]
            ).then(
                fn=lambda: [],
                inputs=None,
                outputs=selected_generated_references
            ).then(
                fn=lambda: "0 selected",
                inputs=None,
                outputs=selected_reference_count
            )
            

            demo.load(
                fn=get_default_project,
                inputs=None,
                outputs=project_dropdown
            ).then(
                fn=load_project_action,
                inputs=project_dropdown,
                outputs=[
                    panel_image,
                    panel_image_text,
                    selected_panel,
                    selected_panel_text,
                    chatbot,
                    conversation_history,
                    generation_request,
                    generated_gallery,
                    generated_reference_metadata
                ]
            )



# ============================================================
# LAUNCH
# ============================================================

demo.launch(css=CUSTOM_CSS)