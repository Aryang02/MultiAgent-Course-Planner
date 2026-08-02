import os
import uuid
from typing import List

from mcp.server.fastmcp import FastMCP

from src.database.session import get_db_session
from src.repositories import ChatRepository, StudyPlanRepository

MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_ORCHESTRATOR_PORT", "8001"))

orchestrator = FastMCP(
    "orchestrator-server",
    host=MCP_HOST,
    port=MCP_PORT,
    stateless_http=True,
)


@orchestrator.tool("get_user_history")
async def get_chat_history(user_id: str, chat_id: str) -> List:
    """Retrieve study history for a user from the DB."""
    with get_db_session() as db:
        chats = ChatRepository(db)
        chat = chats.get_by_chat_id(uuid.UUID(user_id), uuid.UUID(chat_id))
        return chat.messages if chat else []


@orchestrator.tool("create_plan")
def fetch_plan(user_id: str, topic: str):
    with get_db_session() as db:
        plans = StudyPlanRepository(db)
        plan = plans.get_latest_for_topic(uuid.UUID(user_id), topic)
        if not plan:
            return "No plans found, generate a new one."
        return {
            "id": str(plan.id),
            "topic": plan.topic,
            "study_topics": plan.study_topics,
            "notes": plan.notes,
            "test": plan.test,
        }


if __name__ == "__main__":
    orchestrator.run()
