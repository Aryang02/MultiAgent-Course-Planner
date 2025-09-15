from core.models import AgentMessage, AgentRun
from ..base_agent import BaseAgent
from database.db import get_db
from sqlalchemy.orm import Session
from src.utils.mcp_connect import McpConnector
from google.adk.agents.llm_agent import LlmAgent
from src.utils.prompts import CRITIC_SYSTEM_PROMPT, CRITIC_DESCRIPTION

class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(instruction=CRITIC_SYSTEM_PROMPT,
                         description=CRITIC_DESCRIPTION,
                         name="critic")
        self.mcp_client = McpConnector('critic_server')
        self.tools = self.mcp_client.get_tools()

    def critique(self, explanation: str):
        prompt = f"Generate test questions to be given to the user and the answers for them separately based on the following explanation: {explanation}"
        return self.run(prompt)
    
    async def run(self, run_id, prompt, db: Session):

        self.messages = db.query(AgentMessage).filter(run_id = run_id).all()
        self.add_message(self.messages, prompt, "AIMessage")


