import json
import os

class MCPDiscovery:
    def __init__(self, config_file:str=None):
        if config_file is None:
            self.config_file = os.path.join(
                os.path.dirname(__file__), "mcp_config.json"
            )
        else:
            self.config_file = config_file

        self.config = self._load_config()

    def _load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            raise Exception(f"Failed to load MCP config: {str(e)}")
        
    def list_servers(self):
        if 'mcpServers' not in self.config:
            raise Exception("No MCP servers found in config")
        return self.config.get("mcpServers", {})