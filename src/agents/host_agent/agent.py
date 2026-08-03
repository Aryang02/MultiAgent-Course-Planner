from src.agents.base_agent import BaseAgent
from src.agents.agent_executor import AgentExecutor
from src.agents.registry import create_default_executor


class OrchestratorAgent(BaseAgent):
    def __init__(self, executor: AgentExecutor | None = None):
        super().__init__(
            instruction=(
                "You are the orchestrator. Decide which agent to use for each query "
                "and return the final result."
            ),
            description="Router that selects specialist agents for user queries.",
            name="orchestrator",
        )
        self.executor = executor or create_default_executor()

        self._agent_descriptions = {
            name: getattr(agent, "description", name)
            for name, agent in self.executor.agents.items()
        }

    def handle_message(self, message: str) -> str:
        cards_text = "\n".join(
            f"- {name}: {desc}" for name, desc in self._agent_descriptions.items()
        )
        routing_prompt = (
            "You are an orchestrator. Select the best agent for the user message.\n\n"
            f"Available agents:\n{cards_text}\n\n"
            f'User message: "{message}"\n\n'
            "Return ONLY the agent name (tutor, notes, critic, or planner)."
        )
        decision = self.generate(routing_prompt).strip().lower()

        for name in self.executor.agents:
            if name in decision:
                return self.executor.send_message("orchestrator", name, message)

        return f"[Orchestrator] No valid agent found for '{decision}'."
