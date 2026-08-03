from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from settings import settings

APP_URL = settings.APP_URL 

skills = [
    AgentSkill(
        name="create_subtopics",
        description="Create subtopics for a given main topic."
    )
]

tutor_agent_card = AgentCard(
    name="tutor-agent",
    description=(
        "An agent that helps break down main topics into manageable subtopics effectively. "
        "It generates subtopics based on provided main topics and ensures they are relevant and comprehensive."
    ),
    url=f"{APP_URL}:10003",
    capabilities=AgentCapabilities(skills=skills)
)

if __name__ == "__main__":
    print(tutor_agent_card.model_dump_json(indent=2))
