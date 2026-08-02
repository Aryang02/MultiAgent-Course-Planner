from sqlalchemy.orm import Session

from ..base_agent import BaseAgent
from src.core.models import AgentMessage
from src.utils.mcp_utils.mcp_connect import McpConnector
from src.utils.prompts import CRITIC_DESCRIPTION, CRITIC_SYSTEM_PROMPT


class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            instruction=CRITIC_SYSTEM_PROMPT,
            description=CRITIC_DESCRIPTION,
            name="critic",
        )
        self.mcp_client = McpConnector("critic_server")
        self.tools = self.mcp_client.get_tools()

    def critique(self, explanation: str):
        prompt = (
            "Generate test questions to be given to the user and the answers for them "
            f"separately based on the following explanation: {explanation}"
        )
        return self.handle_message(prompt)

    async def run(self, run_id, prompt, db: Session):
        self.messages = db.query(AgentMessage).filter(AgentMessage.run_id == run_id).all()
        return self.handle_message(prompt)
