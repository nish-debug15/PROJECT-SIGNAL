import os
import sys
from dotenv import load_dotenv
from typing import Literal, Optional
from pydantic import BaseModel, Field

from google.adk.agents import Agent
from agents.mock_llm import MockLlm
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

class VerifierOutput(BaseModel):
    decision: Literal["APPROVE", "REJECT"] = Field(description="Decision on the plan")
    reason: str = Field(description="Reason for the decision")
    constraint: Optional[str] = Field(description="Constraint to inject into next run if REJECTED", default=None)

mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_server.main"],
            env={"PYTHONPATH": os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))}
        )
    ),
    tool_filter=["get_junction_signal_state", "get_gtfs_routes"]
)

verifier_agent = Agent(
    name="verifier_agent",
    model=MockLlm(),
    description="Verifier agent to check plans against constraints.",
    instruction=(
        "You are the Verifier Agent for the SIGNAL multi-agent traffic response system. "
        "Your task is to evaluate the provided Rerouting and Signal Timing plan against current ground truth. "
        "Use your tools (get_junction_signal_state, get_gtfs_routes) to check current states of impacted areas. "
        "CRITICAL: If the plan routes traffic into already-critical or highly congested junctions (like Silk Board), you MUST REJECT it. "
        "If you reject, provide a clear 'reason' and formulate a 'constraint' to avoid the issue in the next iteration."
    ),
    tools=[mcp_toolset],
    output_schema=VerifierOutput
)

root_agent = verifier_agent
