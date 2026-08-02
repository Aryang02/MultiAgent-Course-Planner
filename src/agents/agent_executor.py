import inspect
import logging
import uuid
from typing import Any

logger = logging.getLogger(__name__)


class AgentExecutor:
    """Routes calls between agents and logs inter-agent messages."""

    def __init__(self, run_id: uuid.UUID | None = None, log_callback=None):
        self.agents: dict[str, Any] = {}
        self.run_id = run_id
        self._log_callback = log_callback

    def register(self, name: str, handler: object) -> None:
        self.agents[name] = handler

    def _log(self, sender: str, receiver: str, content: dict) -> None:
        if self._log_callback and self.run_id:
            self._log_callback(
                run_id=self.run_id,
                sender=sender,
                receiver=receiver,
                content=content,
            )

    def send_message(self, sender: str, target: str, message: str) -> str:
        handler = self.agents.get(target)
        if handler is None:
            return f"No agent registered for '{target}'"
        self._log(sender, target, {"message": message})
        if hasattr(handler, "handle_message"):
            response = handler.handle_message(message)
        else:
            response = str(handler)
        self._log(target, sender, {"response": response})
        return response

    async def call_agent(
        self,
        sender: str,
        target: str,
        method_name: str,
        *args,
        **kwargs,
    ) -> Any:
        agent = self.agents.get(target)
        if agent is None:
            raise ValueError(f"No agent registered for '{target}'")

        method = getattr(agent, method_name, None)
        if method is None:
            raise ValueError(f"Agent '{target}' has no method '{method_name}'")

        self._log(sender, target, {"method": method_name, "args": str(args)[:500]})

        if inspect.iscoroutinefunction(method):
            result = await method(*args, **kwargs)
        else:
            result = method(*args, **kwargs)

        self._log(target, sender, {"method": method_name, "result": str(result)[:500]})
        return result
