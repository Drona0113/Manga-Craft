# app.py

# 

import gradio as gr

from llm import craft_response
from tools.panel_tools import analyze_panel

def chat_response(message, history, panel_image):
    history = history or []

    response = craft_response(message, history, panel_image)

    user_content = []

    if panel_image:
        user_content.append(
            {"path": panel_image}
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

with gr.Blocks(title="AnimeCraft") as demo:

    # ───────────── Header ─────────────
    gr.Markdown("# ✦ AnimeCraft ✦")
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
                    placeholder="Ask AnimeCraft about your manga panel...",
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
                    inputs=[message, chatbot, panel_image],
                    outputs=chatbot
                )

                # Enter key
                enter_event = message.submit(
                    fn=chat_response,
                    inputs=[message, chatbot, panel_image],
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

demo.launch()