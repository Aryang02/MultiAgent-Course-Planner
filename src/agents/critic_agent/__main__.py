from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from settings import settings

APP_URL = settings.APP_URL 

skills = [
    AgentSkill(
        name="generate_questions",
        description="Generate well-structured list of questions for a given topic from provided source material."
    ),
    AgentSkill(
        name="generate_answers",
        description="Generate well-structured list of answers for given list questions."
    )
]

critic_agent_card = AgentCard(
    name="critic-agent",
    description=(
        "An agent that creates customized questions and answers to help users test their understanding of topics. "
        "It can generate questions based on provided source material and ensure they are relevant and challenging."
    ),
    url=f"{APP_URL}:10004",
    capabilities=AgentCapabilities(skills=skills)
)

if __name__ == "__main__":
    print(critic_agent_card.model_dump_json(indent=2))
