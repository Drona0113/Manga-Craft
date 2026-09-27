#config.py

import os
from dotenv import load_dotenv

load_dotenv(override=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set in the environment variables.")

OPENROUTER_URL = "https://openrouter.ai/api/v1"

MODEL = "google/gemini-2.5-flash-lite"

OPENROUTER_IMAGE_MODEL = "google/gemini-2.5-flash-image"

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# if not GEMINI_API_KEY:
#     raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

# GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

# IMAGE_MODEL = "google/gemini-2.5-flash-image"