"""Routes messages between agents. Full implementation in Phase 4."""


class AgentExecutor:
    def __init__(self):
        self.agents: dict[str, object] = {}

    def register(self, name: str, handler: object) -> None:
        self.agents[name] = handler

    def send_message(self, sender: str, target: str, message: str) -> str:
        handler = self.agents.get(target)
        if handler is None:
            return f"No agent registered for '{target}'"
        if hasattr(handler, "handle_message"):
            return handler.handle_message(message)
        return f"Agent '{target}' cannot handle messages"
