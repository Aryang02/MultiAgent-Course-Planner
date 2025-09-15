from ..base_agent import BaseAgent
from src.utils.mcp_utils.mcp_connect import McpConnector
from src.utils.prompts import NOTES_SYSTEM_PROMPT, NOTES_DESCRIPTION
import uuid

class NotesAgent(BaseAgent):
    def __init__(self):
        super().__init__(instruction=NOTES_SYSTEM_PROMPT,
                         description=NOTES_DESCRIPTION,
                         name="notes")
        self.mcp_client = McpConnector('notes_server')
        self.tools = self.mcp_client.get_tools()

    async def summarize_notes(self, user_id: uuid.UUID, conversation_id: uuid.UUID, notes: str):
        if not self.tools:
            self.tools = await self.mcp_client.refresh_tools()

        self.log_message(user_id, conversation_id, role="user", content=f"Summarize the following notes: {notes}")

        response = await self.run_agent(
            user_id=user_id,
            conversation_id=conversation_id,
            tools=self.tools,
            max_retries=3
        )

        self.log_message(user_id, conversation_id, role="assistant", content=response)

        return response