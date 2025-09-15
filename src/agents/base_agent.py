
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from src.utils.agent_utils.agent_discovery import DiscoveryClient

class BaseAgent:
    def __init__(self, instruction: str, description: str, tools: list[MCPToolset] = [], name: str = "base", cards_path: str):
        self.instruction = instruction
        self.description = description
        self.agent = self._build_agent()
        self.tools = tools
        self.name = name
        self.agent_cards = DiscoveryClient.list_agent_cards(cards_path)

    def _build_agent(self):
        return LlmAgent(
            model='gemini-1.5-pro',
            instruction=self.instruction,
            description=self.description
        )
    
    def handle_message(self, message: str) -> str:
        result = self.agent.run(message)
        return result.get("output") if isinstance(result, dict) else str(result)