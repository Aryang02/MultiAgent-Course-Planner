import uuid

from ..base_agent import BaseAgent
from src.utils.mcp_utils.mcp_connect import McpConnector
from src.utils.prompts import PLANNER_DESCRIPTION, PLANNER_SYSTEM_PROMPT


class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            instruction=PLANNER_SYSTEM_PROMPT,
            description=PLANNER_DESCRIPTION,
            name="planner",
        )
        self.mcp_client = McpConnector("planner_server")
        self.tools = self.mcp_client.get_tools()

    async def create_plan(
        self, user_id: uuid.UUID, conversation_id: uuid.UUID, topic: str, run_id: str
    ):
        if not self.tools:
            self.tools = await self.mcp_client.refresh_tools()

        # Step 1. Call TutorAgent to get topics
        tutor_agent = self.tools["tutor"]
        topics = await tutor_agent.explain(
            topic, caller=self.name, user_id=user_id, conversation_id=conversation_id
        )

        # Step 2. Call NotesAgent to generate notes
        notes_agent = self.tools["notes"]
        notes = await notes_agent.create_notes(
            topics, caller=self.name, user_id=user_id, conversation_id=conversation_id
        )

        # Step 3. Call CriticAgent to create tests
        critic_agent = self.tools["critic"]
        test = await critic_agent.create_test(
            notes, caller=self.name, user_id=user_id, conversation_id=conversation_id
        )

        final_plan = {
            "topic": topic,
            "study_topics": topics,
            "notes": notes,
            "test": test,
        }

        return final_plan
