from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from settings import settings

APP_URL = settings.APP_URL 

skills = [
    AgentSkill(
        name="note_summarization",
        description="Summarize long notes into concise key points."
    ),
    AgentSkill(
        name="note_generation",
        description="Generate well-structured notes from a given topic."
    )
]

notes_agent_card = AgentCard(
    name="notes-agent",
    description=(
        "An agent that helps users manage and summarize their notes effectively. "
        "It can generate notes based on provided topics and ensure they are well-organized."
    ),
    url=f"{APP_URL}:10005",
    capabilities=AgentCapabilities(skills=skills)
)

if __name__ == "__main__":
    print(notes_agent_card.model_dump_json(indent=2))
