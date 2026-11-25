"""
AI Service
Sends chat messages to an LLM through OpenRouter.

OpenRouter exposes an OpenAI-compatible API, so we reuse the `openai`
library and just point it at OpenRouter's base URL.
"""

import os
import logging
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Chat models, tried in order. If the first is rate-limited (429),
# the next one is used automatically.
PRIMARY_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash-lite")
FALLBACK_MODELS = ["google/gemini-2.5-flash"]


def get_model_chain() -> list:
    """Return the ordered list of models to try."""
    chain = [PRIMARY_MODEL]
    for model in FALLBACK_MODELS:
        if model not in chain:
            chain.append(model)
    return chain

_client = None

def get_client() -> AsyncOpenAI:
    """Create (once) and return the OpenRouter client."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set in the environment")
        _client = AsyncOpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)
    return _client

async def generate_reply(messages: list, models: list = None) -> str:
    """
    Send a list of chat messages and return the reply text.

    Tries each model in order. If one fails (e.g. rate-limited, error 429),
    the next model in the chain is tried automatically.

    `messages` is a list of dicts like:
        {"role": "system", "content": "..."}
        {"role": "user", "content": "..."}
    """
    client = get_client()
    model_chain = models or get_model_chain()
    last_error = None

    for model in model_chain:
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
            )
            text = response.choices[0].message.content or ""
            if text.strip():
                return text
        except Exception as error:
            logger.warning("Model %s failed, trying next: %s", model, error)
            last_error = error

    raise last_error or RuntimeError("All models failed to respond")
