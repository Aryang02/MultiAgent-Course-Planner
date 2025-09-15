from a2a.types import AgentCard, AgentSkill, AgentCapabilities
from typing import List
from serializers.agents import AgentCard
from settings import settings
APP_URL = settings.APP_URL

AgentSkill()

AgentCard(
    name="notes-agent",
    description="An agent that helps users manage and summarize their notes effectively. It can generate notes based on provided topics and ensure they are well-organized and easy to understand.",
    url=f"{APP_URL}:10001",
)