from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent
import os
from typing import List
from database.db import get_db
from core.models import ChatHistory, User, StudyPlan

orchestrator = FastMCP("tutor-server", host="localhost", port=8001, stateless_http=True)

@orchestrator.tool("get_user_history")
async def get_chat_history(user_id: str, chat_id: str) -> List:
    """
    Retrieve study history for a user from the DB.
    """
    # Here you’d use SQLAlchemy or raw SQL
    # For now, just mock:
    db = get_db()
    chats = db.query(ChatHistory).filter((ChatHistory.user_id == user_id) and (ChatHistory.chat_id == chat_id)).first().messages
    return chats

@orchestrator.tool("create_plan")
def fetch_plan(user_id: str, topic:str):
    db = get_db
    plans = db.query(StudyPlan).filter((StudyPlan.user_id == user_id) and (topic==topic)).order_by(StudyPlan.updated_at).all()
    if not plans:
        return "No plans found, generate a new one."
    return plans[-1].plan
    