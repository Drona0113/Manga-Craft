# app.py

# 

import gradio as gr

from llm import craft_response
from tools.panel_tools import analyze_panel,composition_analysis

def chat_response(message, history, current_panel):
    history = history or []

    response = craft_response(message, history, current_panel)

    user_content = []

    if current_panel:
        user_content.append(
            {"path": current_panel}
        )

    user_content.append(message)

    return history + [
        {
            "role": "user",
            "content": user_content
        },
        {
            "role": "assistant",
            "content": response
        }
    ]


def analyze_panel_action(panel_image, history):
    history = history or []

    if not panel_image:
        return history + [
            {
                "role": "assistant",
                "content": "Please upload a manga panel first."
            }
        ]

    # Explicitly execute the panel-analysis tool
    result = analyze_panel(panel_image)

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

    if not panel_image:
        return history + [
            {
                "role": "assistant",
                "content": "Please upload a manga panel first."
            }
        ]

    result = composition_analysis(panel_image)

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
        return None, "**Current Panel:** None"

    filename = panel_image.split("\\")[-1]
    return panel_image, f"**Current Panel:** `{filename}`"


def clear_panel():
    return None, "**Current Panel:** None"


def handle_panel_change(panel_image):
    if panel_image is None:
        return None, "**Current Panel:** None"

    return gr.skip(), gr.skip()


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
            current_panel = gr.State(value=None)

            current_panel_text = gr.Markdown("**Current Panel:** None")

            with gr.Row():
                use_panel_btn = gr.Button("📎 Use Panel")
                clear_panel_btn = gr.Button("× Clear")

            use_panel_btn.click(
                fn=use_panel,
                inputs=panel_image,
                outputs=[current_panel, current_panel_text]
            )

            clear_panel_btn.click(
                fn=clear_panel,
                inputs=None,
                outputs=[current_panel, current_panel_text]
            )

            gr.Markdown("### Panel Tools")

            with gr.Row():
                analyze_btn = gr.Button("🔍 Analyze Panel")
                composition_btn = gr.Button("📐 Composition")
            
            generate_btn = gr.Button("🎨 Generate Reference")

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
                    inputs=[message, chatbot, current_panel],
                    outputs=chatbot
                )

                # Enter key
                enter_event = message.submit(
                    fn=chat_response,
                    inputs=[message, chatbot, current_panel],
                    outputs=chatbot
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
                panel_image.change(
                    fn=handle_panel_change,
                    inputs=panel_image,
                    outputs=[current_panel, current_panel_text]
                )
                composition_btn.click(
                    fn=composition_analysis_action,
                    inputs=[panel_image, chatbot],
                    outputs=chatbot
                )

demo.launch()