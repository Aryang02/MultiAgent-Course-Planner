import os

from mcp.server.fastmcp import FastMCP

from src.core.models import AgentMessage
from src.database.db import SessionLocal

MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_CRITIC_PORT", "8004"))

critic = FastMCP("critic-server", host=MCP_HOST, port=MCP_PORT, stateless_http=True)


@critic.tool("get_agent_conversation")
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
    critic.run()
