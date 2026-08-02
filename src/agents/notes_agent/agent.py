from ..base_agent import BaseAgent
from src.agents.utils import parse_json_response
from src.utils.prompts import NOTES_DESCRIPTION, NOTES_SYSTEM_PROMPT


class NotesAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            instruction=NOTES_SYSTEM_PROMPT,
            description=NOTES_DESCRIPTION,
            name="notes",
        )

    def create_notes(self, topics: list[str]) -> dict:
        topics_str = ", ".join(topics)
        prompt = (
            f"Create comprehensive structured study notes for these topics: {topics_str}\n"
            'Return JSON with keys: "summary" (string) and "sections" '
            '(array of objects with "title" and "content").'
        )
        text = self.generate(prompt)
        try:
            parsed = parse_json_response(text)
            if isinstance(parsed, dict):
                return parsed
        except (ValueError, TypeError):
            pass
        return {"summary": text, "sections": []}

    def summarize_notes(self, notes: str) -> str:
        prompt = f"Summarize the following notes concisely:\n{notes}"
        return self.generate(prompt)
