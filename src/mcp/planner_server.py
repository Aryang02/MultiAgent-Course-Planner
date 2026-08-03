import os
import uuid

from mcp.server.fastmcp import FastMCP

from src.auth.authorization import validate_run_belongs_to_user, validate_user_exists
from src.database.session import get_db_session
from src.repositories import AgentRunRepository, StudyPlanRepository

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
    with get_db_session() as db:
        user_uuid = validate_user_exists(db, user_id)
        plans = StudyPlanRepository(db)
        saved = plans.save(
            user_id=user_uuid,
            topic=topic,
            study_topics=study_topics,
            notes=plan,
            test=test,
        )
        return str(saved.id)


@planner.tool("get_agent_conversation")
async def get_agent_conversation(user_id: str, run_id: str):
    with get_db_session() as db:
        run_uuid = validate_run_belongs_to_user(db, user_id, run_id)
        runs = AgentRunRepository(db)
        messages = runs.get_messages(run_uuid)
        return [
            {
                "sender_agent": msg.sender_agent,
                "receiver_agent": msg.receiver_agent,
                "content": msg.content,
            }
            for msg in messages
        ]


if __name__ == "__main__":
    planner.run()
