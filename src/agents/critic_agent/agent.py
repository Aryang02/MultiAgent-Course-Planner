from ..base_agent import BaseAgent
from src.agents.utils import parse_json_response
from src.utils.prompts import CRITIC_DESCRIPTION, CRITIC_SYSTEM_PROMPT


class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            instruction=CRITIC_SYSTEM_PROMPT,
            description=CRITIC_DESCRIPTION,
            name="critic",
        )

    def create_test(self, notes: dict | str) -> dict:
        content = notes if isinstance(notes, str) else str(notes)
        prompt = (
            "Create 5 quiz questions with answers based on the following study material.\n"
            f"{content}\n"
            'Return JSON: {"questions": [{"question": "...", "answer": "..."}]}'
        )
        text = self.generate(prompt)
        try:
            parsed = parse_json_response(text)
            if isinstance(parsed, dict) and "questions" in parsed:
                return parsed
        except (ValueError, TypeError):
            pass
        return {"questions": [], "raw": text}

    def critique(self, explanation: str) -> str:
        prompt = (
            "Generate test questions and separate answers based on this explanation:\n"
            f"{explanation}"
        )
        return self.generate(prompt)
