from mcp.server.fastmcp import FastMCP
from database.db import get_db
from core.models import AgentMessage

critic = FastMCP("critic-server", host="localhost", port=8003, stateless_http=True)

@critic.tool("get_agent_conversation")
async def get_agent_conversation(user_id: str, run_id:str):
    db = get_db()
    messages = db.query(AgentMessage).filter((AgentMessage.run_id == run_id)).order_by(AgentMessage.timestamp).all()
    return [{"sender_agent": msg.sender_agent, "receiver_agent": msg.receiver_agent,"content": msg.content} for msg in messages]