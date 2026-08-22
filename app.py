# app.py

# 

import gradio as gr

from llm import craft_response
from tools.panel_tools import analyze_panel,composition_analysis,generate_reference

def chat_response(message, history, panel_image, selected_panel, conversation_history):

    print("\n========== CHAT RESPONSE ==========")
    print("MESSAGE:", message)
    print("CHATBOT HISTORY:", history)
    print("CONVERSATION HISTORY:", conversation_history)
    print("PANEL IMAGE:", panel_image)
    print("SELECTED PANEL:", selected_panel)
    print("===================================\n")

    history = history or []
    conversation_history = conversation_history or []

    response = craft_response(
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

    print("\n========== UPDATED CONVERSATION HISTORY ==========")
    print(updated_history)
    print("==================================================\n")

    return updated_history, updated_history

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
        return None, "**Selected Panel:** None"

    filename = panel_image.split("\\")[-1]
    return panel_image, f"**Selected Panel:** `{filename}`"


def clear_panel():
    return None, "**Selected Panel:** None"

def update_panel_image_text(panel_image):
    if not panel_image:
        return "**Panel Image:** None"

    filename = panel_image.split("\\")[-1]

    return f"**Panel Image:** `{filename}`"

def generate_reference_action(selected_panel, history):

    print("\n========== GENERATE REFERENCE ==========")
    print("Selected Panel:", selected_panel)

    print("HISTORY VALUE:")
    print(history)

    print("HISTORY TYPE:")
    print(type(history))

    if history:
        print("HISTORY LENGTH:")
        print(len(history))

    print("========================================\n")
    # --------------------------------------------------------
    # Check selected panel
    # --------------------------------------------------------

    if not selected_panel:
        print("❌ No selected panel")
        return None

    # --------------------------------------------------------
    # Check history
    # --------------------------------------------------------

    if not history:
        print("❌ No chatbot history")
        return None

    # --------------------------------------------------------
    # Find the latest textual user request
    # --------------------------------------------------------

    latest_user_message = None

    for chat_message in reversed(history):

        if chat_message["role"] != "user":
            continue

        content = chat_message.get("content")

        # ----------------------------------------------------
        # Normal text message
        # ----------------------------------------------------

        if isinstance(content, str):

            # Ignore Gradio file URLs
            if "/gradio_api/file=" not in content:
                latest_user_message = content
                break

        # ----------------------------------------------------
        # Message containing image + text
        # ----------------------------------------------------

        elif isinstance(content, list):

            text_parts = []

            for item in content:

                # Plain text
                if isinstance(item, str):

                    if "/gradio_api/file=" not in item:
                        text_parts.append(item)

                # Image/file dictionary
                elif isinstance(item, dict):

                    # Ignore image information
                    if "path" in item:
                        continue

                    if "url" in item:
                        continue

            if text_parts:

                latest_user_message = " ".join(text_parts)
                break

    # --------------------------------------------------------
    # Debug extracted request
    # --------------------------------------------------------

    print("\nLATEST USER REQUEST:")
    print(latest_user_message)

    if not latest_user_message:
        print("❌ No user request found")
        return None

    # --------------------------------------------------------
    # Build image-generation prompt
    # --------------------------------------------------------

    prompt = f"""
Create a manga drawing reference based on the selected panel.

User's request:
{latest_user_message}

Preserve the important visual relationships from the selected panel,
including the character pose, composition, perspective, character
placement, and major visual elements unless the user's request
explicitly asks to change them.

Do not introduce unrelated characters or major elements.

Generate the reference according to the user's request.
"""

    # --------------------------------------------------------
    # Debug generation prompt
    # --------------------------------------------------------

    print("\nREFERENCE PROMPT:")
    print(prompt)

    # --------------------------------------------------------
    # Generate reference image
    # --------------------------------------------------------

    result = generate_reference(
        selected_panel,
        prompt
    )

    print("Generated:", result)
    print("========================================\n")

    # --------------------------------------------------------
    # Return generated image path
    # --------------------------------------------------------

    return result
with gr.Blocks(title="MangaCraft") as demo:

    # ───────────── Header ─────────────
    gr.Markdown("# ✦ MangaCraft ✦")
    gr.Markdown("### AI Manga Panel Assistant")

    with gr.Row():

        # ═════════════ LEFT: MANGA WORKSPACE ═════════════
        with gr.Column(scale=1):

            gr.Markdown("## Manga Workspace")

            panel_image = gr.Image(
                label="Panel Preview",
                type="filepath",
                height=400
            )
            panel_image_text = gr.Markdown("**Panel Image:** None")
            selected_panel = gr.State(value=None)
            conversation_history = gr.State(value=[])
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
            generation_output = gr.Image(
                label="Generated Reference",
                type="filepath",
                height=400
            )
            
           


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
                    inputs=[message, chatbot, panel_image,selected_panel,conversation_history],
                    outputs=[chatbot,conversation_history]
                )

                # Enter key
                enter_event = message.submit(
                    fn=chat_response,
                    inputs=[message, chatbot, panel_image,selected_panel,conversation_history],
                    outputs=[chatbot,conversation_history]
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
                    fn=generate_reference_action,
                    inputs=[selected_panel,conversation_history],
                    outputs=generation_output
                )

demo.launch()