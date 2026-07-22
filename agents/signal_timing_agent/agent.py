import os
import sys
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_server.main"],
            env={"PYTHONPATH": os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))}
        )
    ),
    tool_filter=["get_junction_signal_state", "get_gtfs_routes", "list_junctions"]
)

from google.adk.models.google_llm import Gemini
from agents.reliable_llm import ReliableLlm
from agents.mock_llm import MockLlm

real_model = Gemini(model="gemini-2.5-flash")
mock_model = MockLlm()
llm_model = ReliableLlm(real_model=real_model, mock_model=mock_model, agent_name="[Signal Timing]")

signal_timing_agent = Agent(
    name="signal_timing_agent",
    model=llm_model,
    description="An agent to adjust signal timings to alleviate traffic congestion.",
    instruction=(
        "You are the Signal Timing Agent for the SIGNAL multi-agent traffic response system. "
        "Your task is to respond to traffic incidents. "
        "You must analyze the situation by calling the provided tools: list_junctions, get_gtfs_routes, and get_junction_signal_state. "
        "Based on the tool responses, output a signal timing adjustment plan for the affected junctions."
    ),
    tools=[mcp_toolset],
)

root_agent = signal_timing_agent
