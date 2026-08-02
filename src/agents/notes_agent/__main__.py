from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from src.settings import settings

APP_URL = settings.APP_URL

skills = [
    AgentSkill(
        name="create_notes",
        description="Generate structured study notes from topics.",
    )
]

notes_agent_card = AgentCard(
    name="notes-agent",
    description="An agent that generates comprehensive study notes.",
    url=f"{APP_URL}:10005",
    capabilities=AgentCapabilities(skills=skills),
)

if __name__ == "__main__":
    print(notes_agent_card.model_dump_json(indent=2))
