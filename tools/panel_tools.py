# tools/panel_tools.py

from pathlib import Path
from uuid import uuid4

from huggingface_hub import InferenceClient
from openai import OpenAI

import config
from utils.image_utils import encode_image


BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DATA_DIR = BASE_DIR / "data" / "projects"


openrouter = OpenAI(
    api_key=config.OPENROUTER_API_KEY,
    base_url=config.OPENROUTER_URL
)


def analyze_panel(image_path: str) -> str:
    """
    Analyze an uploaded manga panel using a vision-capable model.
    """

    try:
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
Analyze this manga panel for MangaCraft.

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

        if not response.choices:
            raise RuntimeError(
                "The vision model returned no response choices."
            )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "The vision model returned an empty response."
            )

        return content

    except Exception as e:
        print(
            "\n========== PANEL ANALYSIS ERROR =========="
        )
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", str(e))
        print("==========================================\n")

        return (
            "⚠️ Panel analysis failed. "
            "The vision model could not process the panel. "
            "Please try again later."
        )


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

    try:
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

        if not response.choices:
            raise RuntimeError(
                "The vision model returned no response choices."
            )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "The vision model returned an empty response."
            )

        return content

    except Exception as e:
        print(
            "\n========== COMPOSITION ANALYSIS ERROR =========="
        )
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", str(e))
        print("=================================================\n")

        return (
            "⚠️ Composition analysis failed. "
            "The vision model could not analyze the panel. "
            "Please try again later."
        )


COMPOSITION_TOOL = {
    "type": "function",
    "function": {
        "name": "composition_analysis",
        "description": (
            "Use this tool whenever the user asks for composition-specific "
            "analysis of the manga panel. This includes focal point, visual "
            "balance, rule of thirds, leading lines, negative space, depth "
            "planes, foreground/midground/background, visual hierarchy, "
            "viewer eye movement, panel layout, or how the composition "
            "guides attention. The application provides the uploaded panel "
            "automatically. Do not provide an image URL, image path, or "
            "image argument."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    }
}


def generate_reference(
    image_path: str,
    prompt: str,
    project_id: int
) -> str:
    """
    Generate a reference image based on the selected panel
    using Hugging Face image-to-image inference.
    """

    print(
        "\n========== HUGGING FACE IMAGE GENERATION =========="
    )
    print("Model:", config.HF_IMAGE_MODEL)
    print("Input:", image_path)
    print("Prompt:", prompt)
    print("Project:", project_id)
    print("====================================================\n")

    try:
        if not config.HF_TOKEN:
            raise RuntimeError(
                "Hugging Face API token is not configured."
            )

        if not config.HF_IMAGE_MODEL:
            raise RuntimeError(
                "Hugging Face image model is not configured."
            )

        if not image_path:
            raise ValueError(
                "No input image was provided."
            )

        if not Path(image_path).is_file():
            raise FileNotFoundError(
                f"Input image does not exist: {image_path}"
            )

        if not prompt or not prompt.strip():
            raise ValueError(
                "No generation prompt was provided."
            )

        if project_id is None:
            raise ValueError(
                "No project ID was provided."
            )

        client = InferenceClient(
            provider="auto",
            api_key=config.HF_TOKEN
        )

        image = client.image_to_image(
            image=image_path,
            prompt=prompt,
            model=config.HF_IMAGE_MODEL,
        )

        if image is None:
            raise RuntimeError(
                "Hugging Face returned no image."
            )

        generated_references_dir = (
            PROJECT_DATA_DIR
            / str(project_id)
            / "generated_references"
        )

        generated_references_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        generated_image_path = (
            generated_references_dir
            / f"generated_reference_{uuid4().hex}.png"
        )

        image.save(generated_image_path)

        if not generated_image_path.is_file():
            raise RuntimeError(
                "The generated image could not be saved."
            )

        print("✅ Generated reference saved:")
        print(generated_image_path)

        return str(generated_image_path)

    except Exception as e:
        print(
            "\n========== IMAGE GENERATION ERROR =========="
        )
        print("ERROR TYPE:", type(e).__name__)
        print("ERROR:", str(e))
        print("============================================\n")

        return (
            "⚠️ Reference generation failed. "
            "The image generation service could not "
            "generate the reference. Please try again later."
        )


GENERATE_REFERENCE_TOOL = {
    "type": "function",
    "function": {
        "name": "generate_reference",
        "description": (
            "Generate a visual reference image based on the selected image "
            "and the user's requested changes, transformation, artistic style, "
            "or visual purpose. This can be any type of visual art, including "
            "anime, manga, realistic art, comic art, watercolor, digital "
            "painting, concept art, sketch, anatomy reference, pose reference, "
            "lighting study, or other artistic styles. Do not assume manga or "
            "anime style unless the user explicitly requests it. "

            "The application provides the selected image automatically. "
            "Do not provide an image URL or image path. "

            "Preserve important visual relationships such as the main "
            "character/subject, pose, composition, perspective, character "
            "placement, and major visual elements only when the user asks "
            "to preserve them or does not request those elements to change. "

            "Include the user's requested transformation or changes clearly "
            "and specifically. Do not introduce unrelated characters or "
            "major elements. "

            "Only call this tool when the user's reference-generation "
            "request contains enough direction to determine what they want. "

            "For a follow-up message that clearly continues a previous "
            "reference-generation request, combine the current instruction "
            "with the relevant requirements from that previous request. "
            "The previous request and the current message together can "
            "provide sufficient direction for this tool. "

            "For example, if the previous request was to create a realistic "
            "colored reference while preserving the pose and composition, "
            "and the user then says 'use color theory', treat the complete "
            "request as: create that same realistic colored reference, "
            "preserve the pose and composition, and use color theory for "
            "the color choices. Call this tool rather than asking the user "
            "to repeat the previous requirements. "

            "If the user starts a genuinely new reference-generation request "
            "and there is not enough direction in the current request or "
            "relevant conversation context, do NOT call this tool. Instead, "
            "ask one concise clarification question. "

            "Do not invent requirements that were never provided by the user."
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