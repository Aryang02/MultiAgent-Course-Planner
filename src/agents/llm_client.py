import logging

import google.generativeai as genai

from src.settings import settings

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-1.5-pro"


def generate(system_instruction: str, user_prompt: str, model: str = DEFAULT_MODEL) -> str:
    if not settings.GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is not configured")

    genai.configure(api_key=settings.GOOGLE_API_KEY)
    llm = genai.GenerativeModel(model, system_instruction=system_instruction)
    response = llm.generate_content(user_prompt)
    if not response.text:
        raise RuntimeError("Empty response from LLM")
    return response.text.strip()
