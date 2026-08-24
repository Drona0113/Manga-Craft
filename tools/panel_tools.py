# panel_tools.py

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

Return a detailed, structured visual analysis that another LLM
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
        max_completion_tokens=2000
    )

    return response.choices[0].message.content

ANALYZE_PANEL_TOOL = {
    "type": "function",
    "function": {
        "name": "analyze_panel",
        "description": (
        "Use this tool whenever the user asks about visual information "
        "that must be inspected in the manga panel. This is the general "
        "visual analysis tool and can analyze camera angle, shot type, "
        "perspective, framing, composition, character positioning, poses, "
        "body language, facial expressions, background, lighting, visual "
        "depth, spatial relationships, and other observable visual details. "
        "The application provides the panel image automatically. "
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

import base64
import requests


def generate_reference(image_path: str,prompt:str) -> str:
    """
    Generate a manga reference image based on the selected panel.
    """

    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    reference_data_url = f"data:image/jpeg;base64,{image_base64}"

    response = requests.post(
        f"{config.OPENROUTER_URL}/images",
        headers={
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": config.IMAGE_MODEL,

            "prompt": prompt,

            "input_references": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": reference_data_url
                    }
                }
            ],

            "n": 1
        },
        timeout=120
    )

    #response.raise_for_status()
    if response.status_code != 200:

        print("\n========== IMAGE GENERATION ERROR ==========")
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        print("============================================\n")

        if response.status_code == 402:
            return (
                "⚠️ Image generation requires OpenRouter credits. "
                "The Generate Reference tool is configured correctly, "
                "but the image model requires paid usage."
            )

        return f"Image generation failed: {response.text}"

    result = response.json()

    images = result.get("data") or []

    if not images or not images[0].get("b64_json"):
        raise RuntimeError(
            "Image generation succeeded but no image data was returned."
        )

    generated_base64 = images[0]["b64_json"]

    generated_image_path = "generated_reference.png"

    with open(generated_image_path, "wb") as output_file:
        output_file.write(
            base64.b64decode(generated_base64)
        )

    return generated_image_path


GENERATE_REFERENCE_TOOL = {
    "type": "function",
    "function": {
        "name": "generate_reference",
        "description": (
            "Generate a manga drawing reference based on the selected "
            "panel and the user's requested changes. "
            "The application provides the selected panel automatically. "
            "Do not provide an image URL or image path. "
            "The prompt MUST preserve the selected panel's important "
            "visual relationships, including the main character/subject, "
            "pose, composition, perspective, character placement, and "
            "major visual elements unless the user explicitly asks to "
            "change them. "
            "Include the user's requested changes clearly and specifically. "
            "Do not introduce unrelated characters or major elements."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": (
                        "Describe the requested reference image. "
                        "Start from the selected panel and preserve its "
                        "important visual relationships. Clearly describe "
                        "the user's requested changes to camera angle, "
                        "perspective, pose, movement, composition, "
                        "character positioning, lighting, or other visual "
                        "elements. Do not invent unrelated elements."
                    )
                }
            },
            "required": ["prompt"],
            "additionalProperties": False
        }
    }
}
