import os
import sys
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.sequential_agent import SequentialAgent

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import sub-agents
from agents.reroute_agent.agent import root_agent as reroute_agent
from agents.signal_timing_agent.agent import signal_timing_agent

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Step 1: Parallel Execution Agent
parallel_execution_agent = ParallelAgent(
    name="parallel_execution",
    sub_agents=[reroute_agent, signal_timing_agent],
    description="Executes Reroute and Signal-Timing agents in parallel."
)

# Step 2: Coordinator LLM Agent
coordinator_llm_agent = Agent(
    name="coordinator_llm",
    model=LiteLlm(
        model="openrouter/google/gemini-2.5-flash",
        max_tokens=4096,
    ),
    description="Coordinator agent to merge outputs from Reroute and Signal-Timing agents.",
    instruction=(
        "You are the Coordinator Agent for the SIGNAL multi-agent traffic response system. "
        "The Reroute Agent and Signal Timing Agent have just analyzed a traffic incident. "
        "Your task is strictly to merge their outputs into a single cohesive plan. "
        "You must output both the rerouting plan and the signal timing adjustment plan together. "
        "Do not invent new interventions, do not perform second-order checks, and do not reject or retry the plans. "
        "Simply synthesize what the previous agents have output in the history."
    ),
    include_contents='default'
)

# Root Agent: Sequential Agent running Parallel then Coordinator
root_agent = SequentialAgent(
    name="coordinator_flow",
    sub_agents=[parallel_execution_agent, coordinator_llm_agent]
)
