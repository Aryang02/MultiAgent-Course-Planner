from src.settings import settings
from src.utils.mcp_utils.mcp_discovery import MCPDiscovery

MCP_URL_MAP = {
    "orchestrator_server": settings.MCP_ORCHESTRATOR_URL,
    "planner_server": settings.MCP_PLANNER_URL,
    "tutor_server": settings.MCP_TUTOR_URL,
    "critic_server": settings.MCP_CRITIC_URL,
    "notes_server": settings.MCP_NOTES_URL,
}


class McpConnector:
    def __init__(self, server_name: str | None = None, config_file: str | None = None):
        self.discovery = MCPDiscovery(config_file=config_file)
        self.server_name = server_name
        self._connected = False

    def get_server_url(self, server_name: str | None = None) -> str:
        name = server_name or self.server_name
        if not name:
            raise ValueError("server_name is required")
        if name in MCP_URL_MAP:
            return MCP_URL_MAP[name]
        servers = self.discovery.list_servers()
        if name not in servers:
            raise ValueError(f"Unknown MCP server: {name}")
        return servers[name]["args"][0]

    async def connect(self) -> str:
        self._connected = True
        return self.get_server_url()

    def is_connected(self) -> bool:
        return self._connected
