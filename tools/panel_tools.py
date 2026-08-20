from openai import OpenAI

import config
from utils.image_utils import encode_image


openrouter = OpenAI(
    api_key=config.OPENROUTER_API_KEY,
    base_url=config.OPENROUTER_URL
)


def analyze_panel(image_path: str) -> str:
    """
    Analyze an uploaded manga panel using a vision-capable model.
    """

    image_data = encode_image(image_path)

    response = openrouter.chat.completions.create(
        model=config.MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
Analyze this manga panel for AnimeCraft.

Focus on:

- Camera angle
- Shot type
- Perspective
- Composition
- Character positioning
- Body language and facial expressions
- Background/environment
- Lighting
- Important visual details

Do not invent details that are not clearly visible.

Return a concise but useful analysis that another LLM
can use to answer the user's manga-related questions.
"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data
                        }
                    }
                ]
            }
        ],
        max_completion_tokens=1500
    )

    return response.choices[0].message.content

ANALYZE_PANEL_TOOL = {
    "type": "function",
    "function": {
        "name": "analyze_panel",
        "description": (
            "Analyze the manga panel uploaded by the user. "
            "The application provides the uploaded image automatically. "
            "Do not provide an image URL, image path, or image argument."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    }
}

def composition_analysis(image_path: str) -> str:
    """
    Analyze the visual composition of an uploaded manga panel.
    """

    image_data = encode_image(image_path)

    response = openrouter.chat.completions.create(
        model=config.MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
Analyze the composition of this manga panel.

Focus specifically on:

- Rule of thirds
- Focal point
- Visual balance
- Leading lines
- Negative space
- Foreground, midground, and background
- Character placement within the frame
- Size and spatial relationships
- Direction of the viewer's eye movement
- How effectively the composition supports the scene

Do not invent details that are not clearly visible.

Return a concise but useful composition analysis that
another LLM can use to give manga composition advice.
"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data
                        }
                    }
                ]
            }
        ],
        max_completion_tokens=1500
    )

    return response.choices[0].message.content

COMPOSITION_TOOL = {
    "type": "function",
    "function": {
        "name": "composition_analysis",
        "description": (
            "Analyze the visual composition of the manga panel "
            "uploaded by the user. The application provides the "
            "uploaded image automatically."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    }
}