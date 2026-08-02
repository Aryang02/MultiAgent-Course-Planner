import uuid
from typing import Any

from src.agents.llm_client import generate


class BaseAgent:
    def __init__(
        self,
        instruction: str,
        description: str,
        name: str = "base",
    ):
        self.instruction = instruction
        self.description = description
        self.name = name

    def generate(self, user_prompt: str) -> str:
        return generate(system_instruction=self.instruction, user_prompt=user_prompt)

    def handle_message(self, message: str) -> str:
        return self.generate(message)
