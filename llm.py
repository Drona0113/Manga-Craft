# llm.py



from prompts import build_system_prompt
from openai import OpenAI
import config 
from tools.panel_tools import (analyze_panel,ANALYZE_PANEL_TOOL,composition_analysis,COMPOSITION_TOOL)
import json
from utils.image_utils import encode_image

openrouter = OpenAI(
    api_key=config.OPENROUTER_API_KEY,
    base_url=config.OPENROUTER_URL
)



TOOL_MAP = {
    "analyze_panel": analyze_panel,
    "composition_analysis":composition_analysis,
}

tools=[
    ANALYZE_PANEL_TOOL,
    COMPOSITION_TOOL
]

def handle_tool_call(tool_call,panel_image):
    print("🔥 HANDLE TOOL CALL EXECUTED")
    print("TOOL NAME:", tool_call.function.name)
    print("IMAGE:", panel_image)
    
    fn_name = tool_call.function.name

    if fn_name not in TOOL_MAP:
        return {
            "role": "tool",
            "content": f"Error: Tool {fn_name} is not supported",
            "tool_call_id": tool_call.id
        }

    if fn_name in ["analyze_panel", "composition_analysis"] and not panel_image:
        return {
            "role": "tool",
            "content": "No current panel is selected.",
            "tool_call_id": tool_call.id
        }
    args = json.loads(tool_call.function.arguments)
     # The uploaded image comes from the application,not from the LLM.
    if fn_name in ["analyze_panel","composition_analysis"]:
        #args["image_path"] = panel_image
        args = {
        "image_path": panel_image
        }

    result = TOOL_MAP[fn_name](**args)
    print("Tool Result : ",result)

    return {
        "role": "tool",
        "content": str(result),
        "tool_call_id": tool_call.id
    }


def handle_tool_calls(message,panel_image):
    return [
        handle_tool_call(call,panel_image)
        for call in (message.tool_calls or [])
    ]

def clean_history(history):
    cleaned = []

    for h in history:
        content = h["content"]

        if isinstance(content, list):
            text_parts = []

            for item in content:
                if isinstance(item, str):
                    text_parts.append(item)

            content = " ".join(text_parts)

        cleaned.append({
            "role": h["role"],
            "content": content
        })

    return cleaned

def assistant_tool_message(assistant_message):
    return {
        "role": "assistant",
        "content": assistant_message.content,
        "tool_calls": [
            {
                "id": call.id,
                "type": "function",
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments
                }
            }
            for call in (assistant_message.tool_calls or [])
        ]
    }


def craft_response(message, history, panel_image):

    history = clean_history(history)

    relevant_system_prompt = build_system_prompt(message)

    user_content = [
        {
            "type": "text",
            "text": message
        }
    ]

    # IMPORTANT:
    # For now, we are still sending the image to the first LLM.
    # We'll change this architecture after tool calling is stable.
    if panel_image:
        image_data = encode_image(panel_image)

        user_content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": image_data
                }
            }
        )

    messages = (
        [{"role": "system", "content": relevant_system_prompt}]
        + history
        + [{"role": "user", "content": user_content}]
    )

    # ============================================================
    # FIRST LLM CALL
    # ============================================================

    if panel_image:
        response = openrouter.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            max_completion_tokens=2000,
            tools=tools
        )
    else:
        response = openrouter.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            max_completion_tokens=2000
        )

    print("\n========== FIRST LLM RESPONSE ==========")
    print("FINISH REASON:", response.choices[0].finish_reason)
    print("TOOL CALLS:", response.choices[0].message.tool_calls)
    print("MESSAGE:", response.choices[0].message)
    print("========================================\n")

    # ============================================================
    # TOOL-CALL LOOP
    # ============================================================

    while response.choices[0].finish_reason == "tool_calls":

        assistant_message = response.choices[0].message
        # Add the assistant's tool-call message to conversation
        messages.append(
            assistant_tool_message(assistant_message)
        )

        
        # Execute ALL requested tools

        tool_results = handle_tool_calls(
            assistant_message,
            panel_image
        )

        # Add ALL tool results
        messages.extend(tool_results)

       # ========================================================
        # RETURN TOOL RESULTS DIRECTLY
        # ========================================================

        print("\n========== TOOLS EXECUTED ==========")

        for result in tool_results:
            print(
            "TOOL RESULT:",
            result["tool_call_id"],
            "LENGTH:",
            len(result["content"])
            )

        print("=====================================\n")

        for result in tool_results:
            print(
                "TOOL RESULT:",
                result["tool_call_id"],
                "LENGTH:",
                len(result["content"])
            )

        print("=====================================\n")
        # ========================================================
        # SINGLE TOOL → DIRECT TOOL RESULT
        # ========================================================

        if len(tool_results) == 1:
            return tool_results[0]["content"]


# ========================================================
# MULTIPLE TOOLS → SYNTHESIS LLM
# ========================================================

        messages.append({
                "role": "user",
                "content": """
Using the tool results above, answer the user's original request.

Combine the results from ALL tools that were executed.

Preserve the context of the user's original request and conversation history.

Do not ignore any tool result.

Give one coherent answer that is understandable to the user.

Use the tool results as the primary source of visual information.
Do not invent visual details that are not supported by the tool results.
"""
        })
        print("\n🔥 MULTIPLE TOOLS → CALLING SYNTHESIS LLM\n")
        response = openrouter.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            max_completion_tokens=2000
        )

        print("\n========== SYNTHESIS LLM RESPONSE ==========")
        print("FINISH REASON:", response.choices[0].finish_reason)
        print("TOOL CALLS:", response.choices[0].message.tool_calls)
        print("CONTENT:", response.choices[0].message.content)
        print("========================================\n")

    # ============================================================
    # FINAL RESPONSE
    # ============================================================

    final_message = response.choices[0].message

    if final_message.content is None:
        return "I couldn't generate a final response after analyzing the panel."

    return final_message.content

