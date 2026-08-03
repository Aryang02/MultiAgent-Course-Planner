from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from src.settings import settings

APP_URL = settings.APP_URL

skills = [
    AgentSkill(
        name="create_criticism",
        description="Create test questions and answers from study material.",
    )
]

critic_agent_card = AgentCard(
    name="critic-agent",
    description="An agent that generates tests and evaluates study material.",
    url=f"{APP_URL}:10004",
    capabilities=AgentCapabilities(skills=skills),
)

if __name__ == "__main__":
    print(critic_agent_card.model_dump_json(indent=2))
