from ..base_agent import BaseAgent
from src.utils.prompts import TUTOR_DESCRIPTION, TUTOR_SYSTEM_PROMPT
from src.utils.mcp_utils.mcp_connect import McpConnector


class TutorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            instruction=TUTOR_SYSTEM_PROMPT,
            description=TUTOR_DESCRIPTION,
            name="tutor",
        )
        self.mcp_client = McpConnector("tutor_server")
        self.tools = self.mcp_client.get_tools()

    async def explain(self, question: str):
        if not self.tools:
            self.tools = await self.mcp_client.refresh_tools()

        prompt = f"Explain the following concept in simple terms for a student: {question}"
        return self.handle_message(prompt)
