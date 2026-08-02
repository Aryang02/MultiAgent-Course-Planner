import os
import uuid

from mcp.server.fastmcp import FastMCP

from src.auth.authorization import validate_run_belongs_to_user, validate_user_exists
from src.database.session import get_db_session
from src.repositories import AgentRunRepository

MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_TUTOR_PORT", "8003"))

tutor = FastMCP("tutor-server", host=MCP_HOST, port=MCP_PORT, stateless_http=True)


@tutor.tool("search_documents")
async def search_user_documents(user_id: str, query: str, top_k: int = 5):
    """Search a user's uploaded documents for relevant content."""
    from src.database.vector_search import search_documents

    with get_db_session() as db:
        validate_user_exists(db, user_id)
    return search_documents(user_id, query, top_k=top_k)


@tutor.tool("get_agent_conversation")
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
    tutor.run()
