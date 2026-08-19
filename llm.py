# llm.py



from prompts import build_system_prompt
from openai import OpenAI
import config 
from tools.panel_tools import (analyze_panel,ANALYZE_PANEL_TOOL)
import json
from utils.image_utils import encode_image

openrouter = OpenAI(
    api_key=config.OPENROUTER_API_KEY,
    base_url=config.OPENROUTER_URL
)



TOOL_MAP = {
    "analyze_panel": analyze_panel,
}

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

    args = json.loads(tool_call.function.arguments)
     # The uploaded image comes from the application,not from the LLM.
    if fn_name == "analyze_panel":
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

def craft_response(message, history,panel_image):
    #history = [{"role": h["role"], "content": h["content"]} for h in history]
    history = clean_history(history)
    relevant_system_prompt=build_system_prompt(message)
    user_content = [
            {
        "type": "text",
        "text": message
            }
    ]

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

    messages = ([{"role": "system", "content": relevant_system_prompt}] + history + [{"role": "user", "content":user_content}])

    response = openrouter.chat.completions.create(
        model=config.MODEL,
        messages=messages,
        max_completion_tokens=2000,
        
        #stream=True
        
    )
    print("FULL RESPONSE:", response)
    print("FINISH REASON:", response.choices[0].finish_reason)
    print("TOOL CALLS:", response.choices[0].message.tool_calls)
    print("MESSAGE:", response.choices[0].message)

    # full_response = ""

    # for chunk in response:
    #     content = chunk.choices[0].delta.content

    #     if content:
    #         full_response += content
    #         yield full_response
    while response.choices[0].finish_reason == "tool_calls":

        assistant_message = response.choices[0].message

        tool_results = handle_tool_calls(assistant_message,panel_image)

        messages.append(assistant_message)
        messages.extend(tool_results)

        response = openrouter.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=[ANALYZE_PANEL_TOOL],
            max_completion_tokens=2000,
        )

    return response.choices[0].message.content

