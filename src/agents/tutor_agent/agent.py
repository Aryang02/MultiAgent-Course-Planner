from ..base_agent import BaseAgent
from src.agents.utils import parse_json_response
from src.utils.prompts import TUTOR_DESCRIPTION, TUTOR_SYSTEM_PROMPT


class TutorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            instruction=TUTOR_SYSTEM_PROMPT,
            description=TUTOR_DESCRIPTION,
            name="tutor",
        )

    def explain(self, topic: str) -> list[str]:
        prompt = (
            f'Break down the topic "{topic}" into 3-7 study subtopics for a student.\n'
            'Return ONLY a JSON array of strings, e.g. ["Vectors", "Matrices", "Eigenvalues"]'
        )
        text = self.generate(prompt)
        try:
            parsed = parse_json_response(text)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except (ValueError, TypeError):
            pass
        lines = [line.strip().lstrip("-• ") for line in text.splitlines() if line.strip()]
        return lines[:7] if lines else [topic]
