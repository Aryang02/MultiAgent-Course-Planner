from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from src.utils.agent_utils.agent_discovery import DiscoveryClient


class BaseAgent:
    def __init__(
        self,
        instruction: str,
        description: str,
        tools: list[MCPToolset] | None = None,
        name: str = "base",
        cards_path: str | None = None,
    ):
        self.instruction = instruction
        self.description = description
        self.tools = tools or []
        self.name = name
        self.agent = self._build_agent()
        self.agent_cards = []

    def _build_agent(self):
        return LlmAgent(
            model="gemini-1.5-pro",
            instruction=self.instruction,
            description=self.description,
        )

    def handle_message(self, message: str) -> str:
        result = self.agent.run(message)
        return result.get("output") if isinstance(result, dict) else str(result)
