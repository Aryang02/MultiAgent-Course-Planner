import logging

import litellm

from src.observability.metrics import record_llm_tokens
from src.settings import settings

logger = logging.getLogger(__name__)


def _extract_token_usage(response, model: str) -> None:
    usage = getattr(response, "usage", None)
    if not usage:
        return
    prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
    completion_tokens = getattr(usage, "completion_tokens", 0) or 0
    record_llm_tokens(model, prompt_tokens, completion_tokens)


def generate(
    system_instruction: str,
    user_prompt: str,
    model: str | None = None,
) -> str:
    model = model or settings.LLM_MODEL
    response = litellm.completion(
        model=model,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt},
        ],
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS,
    )
    _extract_token_usage(response, model)
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Empty response from LLM")
    return content.strip()
