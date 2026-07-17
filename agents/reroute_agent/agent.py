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
    tool_filter=["get_gtfs_routes", "get_junction_signal_state", "list_zones"]
)

root_agent = Agent(
    name="reroute_agent",
    model=LiteLlm(
        model="openrouter/google/gemini-2.5-flash",
        max_tokens=512,
    ),
    description="An agent to reroute traffic during incidents.",
    instruction=(
        "You are the Reroute Agent for the SIGNAL multi-agent traffic response system. "
        "Your task is to respond to traffic incidents. "
        "You must analyze the situation by calling the provided tools: list_zones, get_gtfs_routes, and get_junction_signal_state. "
        "Based on the tool responses, output a rerouting plan that includes real GTFS route names "
        "(such as 500D, 500C, 335E, 317A) from the zone data. Do not hallucinate any routes."
    ),
    tools=[mcp_toolset],
)
