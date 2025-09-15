
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

class BaseAgent:
    def __init__(self, instruction: str, description: str, tools: list[MCPToolset] = [], name: str = "base"):
        self.instruction = instruction
        self.description = description
        self.agent = self._build_agent()
        self.tools = tools
        self.name = name

    def _build_agent(self):
        return LlmAgent(
            model='gemini-1.5-pro',
            instruction=self.instruction,
            description=self.description
        )