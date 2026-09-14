#config.py

import os
from dotenv import load_dotenv

load_dotenv(override=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set in the environment variables.")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN is not set in the environment variables.")

OPENROUTER_URL = "https://openrouter.ai/api/v1"

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

MODEL = "google/gemini-2.5-flash-lite"

HF_IMAGE_MODEL = "black-forest-labs/FLUX.1-Kontext-dev"

IMAGE_MODEL = "google/gemini-2.5-flash-image"