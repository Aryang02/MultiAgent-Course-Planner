from agents.base_agent import BaseAgent
from agents.agent_executor import AgentExecutor
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset


class OrchestratorAgent(BaseAgent):
    def __init__(self, executor: AgentExecutor):
        super().__init__(
            instruction="You are the orchestrator. Decide which agent card to use for each query and return the final result.",
            description="Router + Executor combined: selects agents and executes via A2A.",
            name="orchestrator",
        )
        self.executor = executor

        # Use cards as context, not tools
        self.cards_text = "\n\n".join(
            [f"Agent: {c['name']}\nDescription: {c.get('description', '')}\nCapabilities: {c.get('capabilities', [])}"
             for c in self.agent_cards]
        )

    def handle_message(self, message: str) -> str:
        """
        Single LLM step:
        1. Decide which agent to call (using cards in context).
        2. Forward to that agent via executor/A2A.
        """
        routing_prompt = f"""
You are an orchestrator agent. Based on the user input, select the most suitable agent.

Available agents:
{self.cards_text}

User message: "{message}"

Return ONLY the agent name to call (from the list above).
"""
        decision = self.agent.run(routing_prompt)
        if isinstance(decision, dict):
            target_agent = decision.get("output", "").strip()
        else:
            target_agent = str(decision).strip()

        if target_agent not in self.executor.agents:
            return f"[Orchestrator] No valid agent found for '{target_agent}'."

        # Forward request to chosen agent
        response = self.executor.send_message("orchestrator", target_agent, message)
        return response
