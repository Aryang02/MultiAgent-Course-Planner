from mcp.server.fastmcp import FastMCP
from database.db import get_db
from core.models import StudyPlan, AgentMessage

planner = FastMCP("planner-server", host="localhost", port=8002, stateless_http=True)

@planner.tool("save-plan")
async def save_plan(plan: dict, test: dict, user_id: str, topic: str, study_topics: list):
    db = get_db()
    generated_plan = StudyPlan(
        user_id=user_id,
        study_topics=study_topics,
        topic=topic,
        plan=plan,
        test=test
    )
    db.add(generated_plan)
    db.commit()
    db.refresh(generated_plan)
    return str(generated_plan.id)

@planner.tool("get_agent_conversation")
async def get_agent_conversation(user_id: str, run_id:str):
    db = get_db()
    messages = db.query(AgentMessage).filter((AgentMessage.run_id == run_id)).order_by(AgentMessage.timestamp).all()
    return [{"sender_agent": msg.sender_agent, "receiver_agent": msg.receiver_agent,"content": msg.content} for msg in messages]