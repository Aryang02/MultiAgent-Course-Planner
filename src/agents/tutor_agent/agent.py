import uuid

from ..base_agent import BaseAgent
from src.agents.utils import parse_json_response
from src.database.vector_search import search_documents
from src.utils.prompts import TUTOR_DESCRIPTION, TUTOR_SYSTEM_PROMPT


class TutorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            instruction=TUTOR_SYSTEM_PROMPT,
            description=TUTOR_DESCRIPTION,
            name="tutor",
        )

    def explain(self, topic: str, user_id: uuid.UUID | None = None) -> list[str]:
        context = ""
        if user_id:
            chunks = search_documents(str(user_id), topic, top_k=5)
            if chunks:
                joined = "\n---\n".join(chunks)
                context = (
                    "\n\nUse the following excerpts from the student's uploaded materials "
                    f"when creating subtopics:\n{joined}\n"
                )

        prompt = (
            f'{context}\nBreak down the topic "{topic}" into 3-7 study subtopics for a student.\n'
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
