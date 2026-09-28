# llm.py

from prompts import SYSTEM_PROMPT
from openai import OpenAI
import config

from tools.panel_tools import (
    analyze_panel,
    ANALYZE_PANEL_TOOL,
    composition_analysis,
    COMPOSITION_TOOL,
    generate_reference,
    GENERATE_REFERENCE_TOOL
)


from tools.project_memory_tools import (
    save_project_memory,
    get_project_memory,
    search_project,
    get_project_context,
    SAVE_PROJECT_MEMORY_TOOL,
    GET_PROJECT_MEMORY_TOOL,
    SEARCH_PROJECT_TOOL,
    GET_PROJECT_CONTEXT_TOOL,
)

import json
from utils.image_utils import encode_image




import time
from collections import defaultdict, deque


# ========================================================
# V2 RATE LIMITING
# ========================================================

RATE_LIMIT_CALLS = 10
RATE_LIMIT_WINDOW = 60

_llm_call_history = defaultdict(deque)


def check_rate_limit(session_id):
    now = time.time()

    calls = _llm_call_history[session_id]

    # Remove calls older than the current window
    while calls and now - calls[0] >= RATE_LIMIT_WINDOW:
        calls.popleft()

    if len(calls) >= RATE_LIMIT_CALLS:

        remaining = int(
            RATE_LIMIT_WINDOW - (now - calls[0])
        )

        return False, remaining

    calls.append(now)

    return True, 0



def openrouter_chat_completion(
    session_id,
    **kwargs
):

    allowed, retry_after = check_rate_limit(
        session_id
    )

    if not allowed:

        print(
            "\n========== RATE LIMIT =========="
        )

        print(
            "SESSION:",
            session_id
        )

        print(
            "STATUS: BLOCKED"
        )

        print(
            "RETRY AFTER:",
            retry_after,
            "seconds"
        )

        print(
            "================================\n"
        )

        raise RuntimeError(
            f"Rate limit reached. "
            f"Please wait about {retry_after} seconds "
            f"before trying again."
        )

    print(
        "\n========== LLM API CALL =========="
    )

    print(
        "SESSION:",
        session_id
    )

    print(
        "CALL COUNT:",
        len(_llm_call_history[session_id]),
        "/",
        RATE_LIMIT_CALLS
    )

    print(
        "STREAM:",
        kwargs.get("stream", False)
    )

    print(
        "===================================\n"
    )

    return openrouter.chat.completions.create(
        **kwargs
    )


def stream_openrouter_chat_completion(
    session_id,
    **kwargs
):

    kwargs["stream"] = True

    return openrouter_chat_completion(
        session_id=session_id,
        **kwargs
    )



def stream_final_response(
    session_id,
    **kwargs
):
    """
    Stream the final user-facing LLM response.

    Yields:
        str: Incremental text chunks.
    """

    full_response = ""

    try:
        stream = stream_openrouter_chat_completion(
            session_id=session_id,
            **kwargs
        )

        for chunk in stream:

            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            content = delta.content

            if content:

                full_response += content

                yield content

        print(
            "\n========== STREAM COMPLETE =========="
        )

        print(
            "FINAL RESPONSE LENGTH:",
            len(full_response)
        )

        print(
            "CONTENT:",
            full_response
        )

        print(
            "====================================\n"
        )

    except Exception as e:

        print(
            "\n========== STREAMING ERROR =========="
        )

        print(
            "ERROR TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            str(e)
        )

        print(
            "====================================\n"
        )

        yield (
            "⚠️ The AI service could not complete the response. "
            "Please try again later."
        )


openrouter = OpenAI(
    api_key=config.OPENROUTER_API_KEY,
    base_url=config.OPENROUTER_URL
)




# ============================================================
# TOOL MAP
# ============================================================

TOOL_MAP = {
    "analyze_panel": analyze_panel,
    "composition_analysis": composition_analysis,
    "generate_reference": generate_reference,

    "save_project_memory": save_project_memory,
    "get_project_memory": get_project_memory,
    "search_project": search_project,
    "get_project_context": get_project_context,
}


ALL_TOOLS = [
    ANALYZE_PANEL_TOOL,
    COMPOSITION_TOOL,
    GENERATE_REFERENCE_TOOL,

    SAVE_PROJECT_MEMORY_TOOL,
    GET_PROJECT_MEMORY_TOOL,
    SEARCH_PROJECT_TOOL,
    GET_PROJECT_CONTEXT_TOOL,
]



# ============================================================
# DETERMINE USER INTENT
# ============================================================

def requires_visual_context(message):

    text = message.lower().strip()

    visual_phrases = [
        "this panel",
        "that panel",
        "the panel",
        "this image",
        "that image",
        "the image",
        "selected panel",
        "selected image",
        "uploaded panel",
        "uploaded image",
        "what is happening",
        "what do you see",
        "analyze",
        "analyse",
        "describe this",
        "composition",
        "camera angle",
        "shot type",
        "perspective",
        "pose",
        "body language",
        "facial expression",
        "lighting",
        "shading",
        "shadow",
        "background",
        "character position",
        "character positioning",
        "visual depth",
        "spatial relationship"
    ]

    return any(
        phrase in text
        for phrase in visual_phrases
    )





def get_tools_for_request(message):

    print("🧠 ALL V2 TOOLS AVAILABLE TO LLM")

    return ALL_TOOLS



# ============================================================
# HANDLE SINGLE TOOL CALL
# ============================================================

def handle_tool_call(
    tool_call,
    panel_image,
    selected_image,
    project_id
):

    print("🔥 HANDLE TOOL CALL EXECUTED")
    print("TOOL NAME:", tool_call.function.name)
    print("PANEL IMAGE:", panel_image)
    print("SELECTED IMAGE:", selected_image)

    fn_name = tool_call.function.name

    # --------------------------------------------------------
    # Check whether tool exists
    # --------------------------------------------------------

    if fn_name not in TOOL_MAP:

        return {
            "role": "tool",
            "content": (
                f"Error: Tool {fn_name} "
                "is not supported"
            ),
            "tool_call_id": tool_call.id
        }

    # --------------------------------------------------------
    # Analyze Panel / Composition
    #
    # IMPORTANT:
    # These tools operate on panel_image.
    # --------------------------------------------------------

    if fn_name in [
        "analyze_panel",
        "composition_analysis"
    ]:

        if not panel_image:

            return {
                "role": "tool",
                "content": (
                    "No uploaded panel image "
                    "is available."
                ),
                "tool_call_id": tool_call.id
            }

    # --------------------------------------------------------
    # Generate Reference
    #
    # IMPORTANT:
    # Generate Reference operates on selected_image.
    # --------------------------------------------------------

    elif fn_name == "generate_reference":

        if not selected_image:

            return {
                "role": "tool",
                "content": (
                    "No panel has been selected with "
                    "📎 Use Panel."
                ),
                "tool_call_id": tool_call.id
            }

    
    # --------------------------------------------------------
    # Get arguments generated by the LLM
    # --------------------------------------------------------

    try:

        args = json.loads(
            tool_call.function.arguments
        )

    except json.JSONDecodeError:

        return {
            "role": "tool",
            "content": (
                "Error: Invalid tool arguments "
                "generated by the model."
            ),
            "tool_call_id": tool_call.id
        }

    # --------------------------------------------------------
    # Inject current project ID for Project Intelligence tools
    # --------------------------------------------------------

    if fn_name in {
        "save_project_memory",
        "get_project_memory",
        "search_project",
        "get_project_context",
    }:
        if project_id is None:
            return {
                "role": "tool",
                "content": "No project is currently selected.",
                "tool_call_id": tool_call.id
            }
        args["project_id"] = project_id

    # --------------------------------------------------------
    # Inject application-controlled image path
    # --------------------------------------------------------

    if fn_name in [
        "analyze_panel",
        "composition_analysis"
    ]:

        # The LLM does NOT provide the image path.
        #
        # The application controls which uploaded
        # panel is analyzed.

        args = {
            "image_path": panel_image
        }

    elif fn_name == "generate_reference":

        # The LLM provides the generation prompt.
        #
        # The application controls which selected
        # panel is used.

        args["image_path"] = selected_image

    # --------------------------------------------------------
    # Execute tool
    # --------------------------------------------------------

    if fn_name == "generate_reference":

        # Do NOT generate the image here.
        #
        # The LLM only prepares the request.
        # Actual generation happens when the user
        # clicks the Generate Reference button.

        result = (
            "Generation request captured successfully. "
            "The reference image will be generated when "
            "the user clicks the Generate Reference button."
        )

    else:

        result = TOOL_MAP[fn_name](**args)

    print("🔥 TOOL RESULT:", result)

    return {
        "role": "tool",
        "content": str(result),
        "tool_call_id": tool_call.id
    }


# ============================================================
# HANDLE ALL TOOL CALLS
# ============================================================

def handle_tool_calls(
    message,
    panel_image,
    selected_image,
    project_id
):

    print("🔥 ENTERING handle_tool_calls")

    results = []

    for call in (message.tool_calls or []):

        print(
            "🔥 ABOUT TO EXECUTE:",
            call.function.name
        )

        result = handle_tool_call(
            call,
            panel_image,
            selected_image,
            project_id
        )

        print(
            "🔥 TOOL FINISHED:",
            call.function.name
        )

        results.append(result)

    print("🔥 LEAVING handle_tool_calls")

    return results


# ============================================================
# CLEAN CHAT HISTORY
# ============================================================

def clean_history(history):

    cleaned = []

    for h in history:

        content = h["content"]

        if isinstance(content, list):

            text_parts = []

            for item in content:

                if isinstance(item, str):
                    text_parts.append(item)

                elif isinstance(item, dict):

                    if item.get("type") == "text":

                        text_parts.append(
                            item.get("text", "")
                        )

            content = " ".join(text_parts)

        cleaned.append({
            "role": h["role"],
            "content": content
        })

    return cleaned


# ============================================================
# CONVERT ASSISTANT TOOL CALL MESSAGE
# ============================================================

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

            for call in (
                assistant_message.tool_calls or []
            )
        ]
    }


print("🚨 NEW LLM.PY VERSION RUNNING")



# ============================================================
# MAIN CHAT FUNCTION
# ============================================================

def craft_response(
    message,
    history,
    panel_image,
    selected_image,
    project_id,
    session_id
):

    generation_request = None

    # ========================================================
    # DETERMINE REQUEST TYPE
    # ========================================================

    needs_visual_context = (
        requires_visual_context(message)
    )

   


    print(
        "\n========== REQUEST ROUTING =========="
    )

    print(
        "MESSAGE:",
        message
    )

    print(
        "NEEDS VISUAL CONTEXT:",
        needs_visual_context
    )

   
   

    # ========================================================
    # VALIDATE REQUIRED PANEL
    # ========================================================

    if needs_visual_context and not selected_image:

        return (
            "Please click **📎 Use Panel** "
            "to select a panel before asking me "
            "to analyze it.",
            None
        )

   

    # ========================================================
    # SELECT TOOLS
    # ========================================================

    request_tools = get_tools_for_request(message)

    print(
        "TOOLS ENABLED:",
        [
            tool["function"]["name"]
            for tool in request_tools
        ]
    )

    print(
        "====================================\n"
    )

    # ========================================================
    # CLEAN PREVIOUS CONVERSATION
    # ========================================================

    history = clean_history(history)


    relevant_system_prompt = SYSTEM_PROMPT

    # ========================================================
    # CURRENT USER MESSAGE
    # ========================================================

    user_content = [
        {
            "type": "text",
            "text": message
        }
    ]

    # --------------------------------------------------------
    # Attach selected panel only when the current request
    # actually requires visual context.
    # --------------------------------------------------------

    if (
        needs_visual_context and selected_image
    ):

        image_data = encode_image(
            selected_image
        )

        user_content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": image_data
                }
            }
        )

        print(
            "🖼️ SELECTED PANEL ATTACHED TO LLM"
        )

    else:
        
        print(
            "📝 NO IMAGE ATTACHED TO LLM"
        )



    # ========================================================
    # BUILD MESSAGES
    # ========================================================

    messages = (
        [
            {
                "role": "system",
                "content": relevant_system_prompt
            }
        ]
        + history
        + [
            {
                "role": "user",
                "content": user_content
            }
        ]
    )

    # ========================================================
    # FIRST LLM CALL
    # ========================================================

    # print("\n========== SYSTEM PROMPT CHECK ==========")
    # print(relevant_system_prompt)
    # print("=========================================\n")

    request_kwargs = {
        "model": config.MODEL,
        "messages": messages,
        "max_completion_tokens": 300
    }

    # --------------------------------------------------------
    # Project-memory tools are available for general requests.
    # The LLM decides whether a tool is actually needed.
    # --------------------------------------------------------

    if request_tools:
        request_kwargs["tools"] = request_tools
        request_kwargs["tool_choice"] = "auto"


    print("\n========== REQUEST SENT TO LLM ==========")

    print("TOOLS SENT:")

    for tool in request_kwargs.get("tools", []):
        print(
            tool["function"]["name"],
            "->",
            tool["function"]["description"]
        )

    print("=========================================\n")
    
    try:

        response = openrouter_chat_completion(
            session_id=session_id,
            **request_kwargs
        )

    except RuntimeError as e:

        # Rate-limit errors are already user-friendly.
        # Keep them separate from API/service failures.

        error_message = str(e)

        print(
            "\n========== LLM REQUEST ERROR =========="
        )

        print(
            "ERROR TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            error_message
        )

        print(
            "=======================================\n"
        )

        return (
            f"⚠️ {error_message}",
            None
        )

    except Exception as e:

        print(
            "\n========== LLM API ERROR =========="
        )

        print(
            "ERROR TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            str(e)
        )

        print(
            "===================================\n"
        )

        return (
            "⚠️ The AI service could not process your request. "
            "Please try again later.",
            None
        )


    # ========================================================
    # DEBUG FIRST RESPONSE
    # ========================================================

    print(
        "\n========== FIRST LLM RESPONSE =========="
    )

    print(
        "FINISH REASON:",
        response.choices[0].finish_reason
    )

    print(
        "TOOL CALLS:",
        response.choices[0].message.tool_calls
    )

    for call in (
        response.choices[0].message.tool_calls or []
    ):

        print("\n🔥 TOOL NAME:")
        print(call.function.name)

        print("🔥 TOOL ARGUMENTS:")
        print(call.function.arguments)

    print(
        "MESSAGE:",
        response.choices[0].message
    )

    print(
        "========================================\n"
    )

    # ========================================================
    # DIRECT LLM RESPONSE
    # ========================================================

    if response.choices[0].finish_reason != "tool_calls":

        direct_response = (
            response.choices[0].message.content
        )

        print(
            "\n🟢 DIRECT LLM RESPONSE — NO TOOL CALL"
        )

        print(
            direct_response
        )

        print(
            "====================================\n"
        )

        return (
            direct_response,
            None
        )


    # ========================================================
    # TOOL-CALL LOOP
    # ========================================================

    while (
        response.choices[0].finish_reason
        == "tool_calls"
    ):

        assistant_message = (
            response.choices[0].message
        )

        # ----------------------------------------------------
        # Capture generation request
        # ----------------------------------------------------

        for call in (
            assistant_message.tool_calls or []
        ):

            if (
                call.function.name
                == "generate_reference"
            ):

                try:

                    args = json.loads(
                        call.function.arguments
                    )

                    generation_request = (
                        args.get("prompt")
                    )

                except json.JSONDecodeError:

                    generation_request = None

                print(
                    "\n🎨 GENERATION REQUEST CAPTURED:"
                )

                print(
                    generation_request
                )

                print(
                    "================================\n"
                )

        # ----------------------------------------------------
        # Add assistant tool-call message
        # ----------------------------------------------------

        messages.append(
            assistant_tool_message(
                assistant_message
            )
        )

        # ----------------------------------------------------
        # Execute requested tools
        # ----------------------------------------------------

        tool_results = handle_tool_calls(
            assistant_message,
            panel_image,
            selected_image,
            project_id
        )

        # ----------------------------------------------------
        # Add tool results
        # ----------------------------------------------------

        messages.extend(
            tool_results
        )

        # ====================================================
        # GENERATE REFERENCE
        # ====================================================

        if generation_request:

            print(
                "\n🎨 GENERATION REQUEST READY"
            )

            return (
                "🎨 Generation request captured!\n\n"
                "Click **Generate Reference** in "
                "the Panel Tools to create the image.",
                generation_request
            )

        # ====================================================
        # TOOL RESULTS → LLM
        # ====================================================

        messages.append(
            {
                "role": "user",
                "content": (
                    "Answer the user's original "
                    "request using the tool results "
                    "above."
                )
            }
        )


        print(
            "\n🔥 TOOL RESULTS READY FOR "
            "FINAL STREAMING RESPONSE\n"
        )

        break

      
    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    response_stream = stream_final_response(
        session_id=session_id,
        model=config.MODEL,
        messages=messages,
        max_completion_tokens=1200
    )

    return (
        response_stream,
        generation_request
    )

    