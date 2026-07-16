import os
import sys
import asyncio
import json
from dotenv import load_dotenv

from google.genai import types
from google.adk.agents import Agent
from agents.mock_llm import MockLlm
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from agents.reroute_agent.agent import root_agent as reroute_agent
from agents.signal_timing_agent.agent import signal_timing_agent
from agents.verifier.agent import verifier_agent

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
    model=MockLlm(),
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
coordinator_flow = SequentialAgent(
    name="coordinator_flow",
    sub_agents=[parallel_execution_agent, coordinator_llm_agent]
)

root_agent = coordinator_flow

async def main():
    if len(sys.argv) < 2:
        print("Usage: python agent.py <incident_description>")
        sys.exit(1)
        
    incident_desc = sys.argv[1]
    
    # 1. Initialize ADK Runner and Session
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="coordinator_app",
        agent=coordinator_flow,
        session_service=session_service
    )
    
    # Create session
    session = await runner.session_service.create_session(app_name="coordinator_app", user_id="cli_user")
    
    max_retries = 3
    current_attempt = 1
    
    # Initial trigger message
    msg_text = f"New Incident: {incident_desc}"
    
    while current_attempt <= max_retries:
        print(f"\n=== Attempt {current_attempt} ===")
        
        # We must clear the agent states in the session to ensure the SequentialAgent and its sub-agents run again
        session = await runner.session_service.get_session(app_name="coordinator_app", user_id="cli_user", session_id=session.id)
        if "_adk_agent_states" in session.state:
            del session.state["_adk_agent_states"]
        if "_adk_end_of_agents" in session.state:
            del session.state["_adk_end_of_agents"]
        
        # Run Coordinator Flow
        print("Running Coordinator Flow (Parallel Delegation + Merge)...")
        plan_output = ""
        user_msg = types.Content(role="user", parts=[types.Part.from_text(text=msg_text)])
        
        async for event in runner.run_async(user_id="cli_user", session_id=session.id, new_message=user_msg):
            if event.content and event.author == "coordinator_llm":
                if event.content.parts and event.content.parts[0].text:
                    plan_output += event.content.parts[0].text
        
        print(f"\n--- Coordinator Merged Plan ---\n{plan_output}\n-------------------------------\n")
        
        # Run Verifier
        print("Running Verifier...")
        # Since the verifier is a single_turn agent, we can run it isolated using a new Runner and Session to avoid polluting history
        # Or we can run it in the same session, but the output schema returns JSON.
        verifier_runner = Runner(
            app_name="verifier_app",
            agent=verifier_agent,
            session_service=InMemorySessionService()
        )
        v_session = await verifier_runner.session_service.create_session(app_name="verifier_app", user_id="cli_user")
        
        verifier_input = types.Content(role="user", parts=[types.Part.from_text(text=f"Incident: {incident_desc}\n\nProposed Plan:\n{plan_output}")])
        
        v_output = ""
        async for event in verifier_runner.run_async(user_id="cli_user", session_id=v_session.id, new_message=verifier_input):
            if event.content and event.author == "verifier_agent":
                if event.content.parts and event.content.parts[0].text:
                    v_output += event.content.parts[0].text
                
        print(f"Verifier Raw Output: {v_output}")
        
        try:
            # ADK single_turn with output_schema guarantees JSON string
            v_json = json.loads(v_output)
            decision = v_json.get("decision")
            reason = v_json.get("reason")
            constraint = v_json.get("constraint")
        except json.JSONDecodeError:
            print("Failed to parse Verifier output as JSON.")
            decision = "REJECT"
            reason = "Failed to parse JSON"
            constraint = "Return valid JSON"
            
        print(f"\nVerifier Decision: {decision}")
        print(f"Reason: {reason}")
        if constraint:
            print(f"Constraint: {constraint}")
            
        if decision == "APPROVE":
            print("\nFinal Plan Approved!")
            break
        else:
            print(f"\nPlan Rejected. Retrying...")
            msg_text = f"The previous plan was REJECTED by the verifier.\nReason: {reason}\nCONSTRAINT FOR NEXT ITERATION: {constraint}\nCRITICAL: You MUST explicitly output a revised rerouting and signal timing plan that STRICTLY follows this constraint. Do NOT provide ambiguous advice or suspend routes without concrete detours. Specify exact alternative routes."
            current_attempt += 1
            
    if current_attempt > max_retries:
        print("\n=== MAX RETRIES REACHED ===")
        print("Unable to verify safe plan. The system failed to find an acceptable response within the retry limit.")
        
if __name__ == "__main__":
    asyncio.run(main())
