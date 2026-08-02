import os
from typing import List

from mcp.server.fastmcp import FastMCP

from src.core.models import ChatHistory, StudyPlan
from src.database.db import SessionLocal

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
    db = SessionLocal()
    try:
        chat = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id, ChatHistory.chat_id == chat_id)
            .first()
        )
        return chat.messages if chat else []
    finally:
        db.close()


@orchestrator.tool("create_plan")
def fetch_plan(user_id: str, topic: str):
    db = SessionLocal()
    try:
        plans = (
            db.query(StudyPlan)
            .filter(StudyPlan.user_id == user_id, StudyPlan.topic == topic)
            .order_by(StudyPlan.updated_at)
            .all()
        )
        if not plans:
            return "No plans found, generate a new one."
        return plans[-1]
    finally:
        db.close()


if __name__ == "__main__":
    orchestrator.run()
