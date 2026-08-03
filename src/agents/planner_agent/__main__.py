from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from src.settings import settings

APP_URL = settings.APP_URL

skills = [
    AgentSkill(
        name="create_study_plan",
        description="Create a structured study plan for a given topic.",
    )
]

planner_agent_card = AgentCard(
    name="planner-agent",
    description=(
        "An agent that plans the course of study for users effectively. "
        "It generates study plans based on provided topics."
    ),
    url=f"{APP_URL}:10002",
    capabilities=AgentCapabilities(skills=skills),
)

if __name__ == "__main__":
    print(planner_agent_card.model_dump_json(indent=2))
