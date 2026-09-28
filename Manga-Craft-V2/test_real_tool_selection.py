import sys
import base64
import mimetypes

import llm
import config
from openai import OpenAI


openrouter = OpenAI(
    api_key=config.OPENROUTER_API_KEY,
    base_url=config.OPENROUTER_URL
)


def encode_image_for_test(image_path):
    mime_type, _ = mimetypes.guess_type(image_path)

    if mime_type is None:
        mime_type = "image/jpeg"

    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    return f"data:{mime_type};base64,{image_data}"


def run_test(name, message, tools, expected, image_path=None):
    print("\n" + "=" * 70)
    print("TEST:", name)
    print("MESSAGE:", message)
    print("EXPECTED:", expected)

    user_content = [
        {
            "type": "text",
            "text": message
        }
    ]

    if image_path:
        user_content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": encode_image_for_test(image_path)
                }
            }
        )

        print("🖼️ IMAGE ATTACHED")

    response = openrouter.chat.completions.create(
        model=config.MODEL,
        messages=[
            {
                "role": "system",
                "content": llm.SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_content
            }
        ],
        tools=tools,
        tool_choice="auto",
        max_completion_tokens=200,
    )

    assistant_message = response.choices[0].message

    print(
        "FINISH REASON:",
        response.choices[0].finish_reason
    )

    if not assistant_message.tool_calls:
        print("❌ NO TOOL CALL")
        print(
            "MODEL RESPONSE:",
            assistant_message.content
        )
        return False

    selected_tools = [
        call.function.name
        for call in assistant_message.tool_calls
    ]

    print("SELECTED TOOLS:", selected_tools)

    if expected in selected_tools:
        print("✅ PASS")
        return True

    print("❌ FAIL")
    return False


# ---------------------------------------------------------
# Image path
# ---------------------------------------------------------

if len(sys.argv) < 2:
    print(
        "\n❌ Please provide the path to a manga panel image."
    )
    print(
        r'Example: python test_real_tool_selection.py "D:\path\to\panel.png"'
    )
    sys.exit(1)

IMAGE_PATH = sys.argv[1]


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

tests = [
    {
        "name": "SAVE MEMORY",
        "message": "Kageyama always wears a black jacket.",
        "tools": [
            llm.SAVE_PROJECT_MEMORY_TOOL,
            llm.GET_PROJECT_MEMORY_TOOL,
        ],
        "expected": "save_project_memory",
    },

    {
        "name": "GET MEMORY",
        "message": (
            "Show me all the memories currently saved in this project"
        ),
        "tools": [
            llm.SAVE_PROJECT_MEMORY_TOOL,
            llm.GET_PROJECT_MEMORY_TOOL,
        ],
        "expected": "get_project_memory",
    },

    {
        "name": "SEARCH PROJECT",
        "message": (
            "Search the project for information about Kageyama's jacket."
        ),
        "tools": [
            llm.SEARCH_PROJECT_TOOL,
            llm.GET_PROJECT_CONTEXT_TOOL,
        ],
        "expected": "search_project",
    },

    {
        "name": "GET PROJECT CONTEXT",
        "message": (
            "Give me the relevant context for this project."
        ),
        "tools": [
            llm.SEARCH_PROJECT_TOOL,
            llm.GET_PROJECT_CONTEXT_TOOL,
        ],
        "expected": "get_project_context",
    },

    {
        "name": "VISUAL ANALYSIS",
        "message": "Analyze this panel.",
        "tools": [
            llm.ANALYZE_PANEL_TOOL,
            llm.COMPOSITION_TOOL,
        ],
        "expected": "analyze_panel",
        "image": True,
    },

    {
        "name": "COMPOSITION",
        "message": "Analyze the composition of this panel.",
        "tools": [
            llm.ANALYZE_PANEL_TOOL,
            llm.COMPOSITION_TOOL,
        ],
        "expected": "composition_analysis",
        "image": True,
    },

    {
        "name": "REFERENCE",
        "message": (
            "Generate a reference where Kageyama "
            "is standing in front of the school."
        ),
        "tools": [
            llm.GENERATE_REFERENCE_TOOL,
        ],
        "expected": "generate_reference",
        "image": True,
    },
]

passed = 0

for test in tests:
    image_path = IMAGE_PATH if test.get("image") else None

    if run_test(
        test["name"],
        test["message"],
        test["tools"],
        test["expected"],
        image_path
    ):
        passed += 1


print("\n" + "=" * 70)
print(
    f"RESULT: {passed}/{len(tests)} RETESTS PASSED"
)

if passed == len(tests):
    print("🎉 ALL FAILED CASES ARE NOW FIXED")
else:
    print("⚠️ SOME CASES STILL NEED ATTENTION")