import os

from mcp.server.fastmcp import FastMCP

from src.core.models import AgentMessage, StudyPlan
from src.database.db import SessionLocal

MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PLANNER_PORT", "8002"))

planner = FastMCP("planner-server", host=MCP_HOST, port=MCP_PORT, stateless_http=True)


@planner.tool("save-plan")
async def save_plan(
    plan: dict,
    test: dict,
    user_id: str,
    topic: str,
    study_topics: list,
):
    db = SessionLocal()
    try:
        generated_plan = StudyPlan(
            user_id=user_id,
            study_topics=study_topics,
            topic=topic,
            notes=plan,
            test=test,
        )
        db.add(generated_plan)
        db.commit()
        db.refresh(generated_plan)
        return str(generated_plan.id)
    finally:
        db.close()


@planner.tool("get_agent_conversation")
async def get_agent_conversation(user_id: str, run_id: str):
    db = SessionLocal()
    try:
        messages = (
            db.query(AgentMessage)
            .filter(AgentMessage.run_id == run_id)
            .order_by(AgentMessage.timestamp)
            .all()
        )
        return [
            {
                "sender_agent": msg.sender_agent,
                "receiver_agent": msg.receiver_agent,
                "content": msg.content,
            }
            for msg in messages
        ]
    finally:
        db.close()


if __name__ == "__main__":
    planner.run()
