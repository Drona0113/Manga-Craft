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
    delete_project
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
    get_generated_references
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

    

def use_generated(generated_image):
    if not generated_image:
        return None, "**Selected Panel:** None"

    filename = generated_image.split("\\")[-1]

    return (
        generated_image,
        f"**Selected Panel:** `{filename}`"
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

    projects = get_projects()

    if not projects:
        return None

    project = projects[0]

    return f"{project['id']} | {project['name']}"



def create_project_action(project_name):

    if not project_name or not project_name.strip():

        return (
            gr.update(),
            None,
            "⚠️ Please enter a project name."
        )

    project_name = project_name.strip()

    project_id = create_project(project_name)

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

    for reference in references:

        reference_path = reference["file_path"]

        generated_references.append(
            reference_path
        )

    print("GENERATED REFERENCES:", len(generated_references))

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
        generated_references
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

with gr.Blocks(title="MangaCraft") as demo:
    generation_popup = gr.Markdown(
    "",
    visible=False
    )
    # ───────────── Header ─────────────
    gr.Markdown("# ✦ MangaCraft ✦")
    gr.Markdown("### AI Manga Panel Assistant")

    with gr.Row():

        # ═════════════ LEFT: MANGA WORKSPACE ═════════════
        with gr.Column(scale=1):

            gr.Markdown("## Manga Workspace")
            gr.Markdown("### 📁 Projects")

            project_dropdown = gr.Dropdown(
                label="Current Project",
                choices=load_projects(),
                value=None,
                interactive=True
            )
            

            with gr.Row():

                new_project_name = gr.Textbox(
                    placeholder="New project name...",
                    label="",
                    scale=4
                )

                create_project_btn = gr.Button(
                    "＋ Create",
                    scale=1
                )

            project_status = gr.Markdown("")

            with gr.Row():

                rename_project_name = gr.Textbox(
                    placeholder="Rename selected project...",
                    label="",
                    scale=4
                )

                rename_project_btn = gr.Button(
                    "Rename",
                    scale=1
                )

            delete_project_btn = gr.Button(
                "🗑 Delete Project"
            )
            panel_image = gr.Image(
                label="Panel Preview",
                type="filepath",
                height=400
            )
            panel_image_text = gr.Markdown("**Panel Image:** None")
            selected_panel = gr.State(value=None)
            generation_request = gr.State(value=None)
            generated_image=gr.State(value=None)
            conversation_history = gr.State(value=[])
            current_project_id = gr.State(value=None)
            selected_panel_text = gr.Markdown("**Selected Panel:** None")

            panel_image.change(
                fn=update_panel_image_text,
                inputs=panel_image,
                outputs=panel_image_text
            )

            with gr.Row():
                use_panel_btn = gr.Button("📎 Use Panel")
                clear_panel_btn = gr.Button("× Clear")

            use_panel_btn.click(
                fn=use_panel,
                inputs=panel_image,
                outputs=[selected_panel, selected_panel_text]
            )

            clear_panel_btn.click(
                fn=clear_panel,
                inputs=None,
                outputs=[selected_panel, selected_panel_text]
            )

            gr.Markdown("### Panel Tools")

            with gr.Row():
                analyze_btn = gr.Button("🔍 Analyze Panel")
                composition_btn = gr.Button("📐 Composition")
            
            generate_btn = gr.Button("🎨 Generate Reference")
            generated_gallery = gr.Gallery(
                label="Generated References",
                columns=3,
                rows=1,
                height=220,
                object_fit="contain",
                allow_preview=True
            )
            # generation_output = gr.Image(
            #     label="Generated Reference",
            #     type="filepath",
            #     height=400
            # )
            use_generated_btn = gr.Button("📎 Use Generated")
            
           


        # ═════════════ RIGHT: AI ASSISTANT ═════════════
        with gr.Column(scale=1):

            gr.Markdown("## AI Assistant")

            chatbot = gr.Chatbot(
                label="Conversation",
                height=480,
               
            )

            with gr.Row():

                message = gr.Textbox(
                    placeholder="Ask MangaCraft about your manga panel...",
                    label="",
                    scale=5,
                    lines=1
                )

                send_btn = gr.Button(
                    "➤ Send",
                    scale=1,
                    min_width=100
                )

                # Send button
                send_event = send_btn.click(
                    fn=chat_response,
                    inputs=[message, chatbot, panel_image,selected_panel,conversation_history,project_dropdown],
                    outputs=[chatbot,conversation_history,generation_request]
                )

                # Enter key
                enter_event = message.submit(
                    fn=chat_response,
                    inputs=[message, chatbot, panel_image,selected_panel,conversation_history,project_dropdown],
                    outputs=[chatbot,conversation_history,generation_request]
                )

                # Clear textbox after sending
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
                #Analyse Panel button
                analyze_btn.click(
                        fn=analyze_panel_action,
                        inputs=[panel_image, chatbot],
                        outputs=chatbot
                )
                
                composition_btn.click(
                    fn=composition_analysis_action,
                    inputs=[panel_image, chatbot],
                    outputs=chatbot
                )

                generate_btn.click(
                    fn=test_generate_reference_action,
                    inputs=[
                        project_dropdown,
                        selected_panel,
                        generation_request
                    ],
                    outputs=generated_gallery
                )
                use_generated_btn.click(
                    fn=use_generated,
                    inputs=generated_image,
                    outputs=[selected_panel, selected_panel_text]
                )

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

                project_dropdown.change(
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
                        generated_gallery
                    ]
                )
                # demo.load(
                #     fn=load_project_action,
                #     inputs=project_dropdown,
                #     outputs=[
                #         current_project_id,
                #         selected_panel,
                #         panel_image,
                #         conversation_history,
                #         generation_request,
                #         generated_image,
                #         selected_panel_text,
                #         panel_image_text,
                #         project_status
                #     ]
                # )


demo.launch()