from mcp_discovery import MCPDiscovery
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

class McpConnector:

    def __init__(self, config_file, server_name=None):
        self.discovery = MCPDiscovery(config_file=config_file)
        self.tools = list[MCPToolset] = []
        self._load_all_tools()
        self.server_name = server_name

    async def _load_all_tools(self):
        tools = []
        try:
            for server_name, server_info in self.discovery.list_servers():
                if self.server_name != server_name:
                    continue
                conn = StreamableHTTPServerParams(url=server_info["args"][0])
                
                toolset = MCPToolset(connection_params=conn)
                tool = await toolset.get_tools()

                tools.append[toolset]
            self.tools = tools

        except Exception as e:
            raise Exception(f"Failed to load MCP tools: {str(e)}")
    
    def get_tools(self):
        return self.tools.copy()
    
    async def refresh_tools(self):
        self.tools = []
        await self._load_all_tools()
        return self.tools.copy()