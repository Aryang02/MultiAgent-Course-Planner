from src.utils.mcp_utils.mcp_discovery import MCPDiscovery
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams


class McpConnector:
    def __init__(self, server_name: str | None = None, config_file: str | None = None):
        self.discovery = MCPDiscovery(config_file=config_file)
        self.server_name = server_name
        self.tools: list[MCPToolset] = []

    async def connect(self) -> list[MCPToolset]:
        tools: list[MCPToolset] = []
        for name, server_info in self.discovery.list_servers().items():
            if self.server_name and self.server_name != name:
                continue
            conn = StreamableHTTPServerParams(url=server_info["args"][0])
            toolset = MCPToolset(connection_params=conn)
            await toolset.get_tools()
            tools.append(toolset)
        self.tools = tools
        return tools

    def get_tools(self) -> list[MCPToolset]:
        return self.tools.copy()

    async def refresh_tools(self) -> list[MCPToolset]:
        self.tools = []
        return await self.connect()
