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

planner_agent_card = AgentCard(
    name="notes-agent",
    description=(
        "An agent that plans the course of study for users effectively. "
        "It can generate study plans based on provided topic and ensure they are well-organized."
    ),
    url=f"{APP_URL}:10002",
    capabilities=AgentCapabilities(skills=skills)
)

if __name__ == "__main__":
    print(planner_agent_card.model_dump_json(indent=2))
