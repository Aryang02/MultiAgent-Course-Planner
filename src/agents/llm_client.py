import logging
import time

import google.generativeai as genai

from src.observability.metrics import record_llm_tokens
from src.settings import settings

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-1.5-pro"


def _extract_token_usage(response, model: str) -> None:
    usage = getattr(response, "usage_metadata", None)
    if not usage:
        return
    prompt_tokens = getattr(usage, "prompt_token_count", 0) or 0
    completion_tokens = getattr(usage, "candidates_token_count", 0) or 0
    record_llm_tokens(model, prompt_tokens, completion_tokens)


def generate(system_instruction: str, user_prompt: str, model: str = DEFAULT_MODEL) -> str:
    if not settings.GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is not configured")

    genai.configure(api_key=settings.GOOGLE_API_KEY)
    llm = genai.GenerativeModel(model, system_instruction=system_instruction)
    response = llm.generate_content(user_prompt)
    _extract_token_usage(response, model)
    if not response.text:
        raise RuntimeError("Empty response from LLM")
    return response.text.strip()
