import uuid

from ..base_agent import BaseAgent
from src.agents.agent_executor import AgentExecutor
from src.utils.prompts import PLANNER_DESCRIPTION, PLANNER_SYSTEM_PROMPT


class PlannerAgent(BaseAgent):
    def __init__(self, executor: AgentExecutor):
        super().__init__(
            instruction=PLANNER_SYSTEM_PROMPT,
            description=PLANNER_DESCRIPTION,
            name="planner",
        )
        self.executor = executor

    async def create_plan(
        self,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        topic: str,
        run_id: uuid.UUID,
    ) -> dict:
        study_topics = await self.executor.call_agent(
            "planner", "tutor", "explain", topic, user_id=user_id
        )
        notes = await self.executor.call_agent(
            "planner", "notes", "create_notes", study_topics
        )
        test = await self.executor.call_agent(
            "planner", "critic", "create_test", notes
        )

        return {
            "topic": topic,
            "study_topics": study_topics,
            "notes": notes,
            "test": test,
            "run_id": str(run_id),
            "user_id": str(user_id),
            "chat_id": str(conversation_id),
        }
