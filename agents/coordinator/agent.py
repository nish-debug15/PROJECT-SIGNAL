import os
import sys
import asyncio
import json
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

from google.genai import types
from google.adk.agents import Agent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from agents.logger import AgentLogger

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

from google.adk.models.google_llm import Gemini
from agents.reliable_llm import ReliableLlm
from agents.mock_llm import MockLlm

real_model = Gemini(model="gemini-2.5-flash")
mock_model = MockLlm()
llm_model = ReliableLlm(real_model=real_model, mock_model=mock_model, agent_name="[Coordinator]")

# Step 2: Coordinator LLM Agent
coordinator_llm_agent = Agent(
    name="coordinator_llm",
    model=llm_model,
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

async def run_incident_response(incident_desc: str):
    AgentLogger().emit_event("System", "Started Incident Response", incident_desc)
    
    # 1. Initialize ADK Runner and Session
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="coordinator_app",
        agent=coordinator_flow,
        session_service=session_service
    )
    
    import uuid
    run_id = f"demo_user_{uuid.uuid4().hex[:8]}"
    
    # Create session
    session = await runner.session_service.create_session(app_name="coordinator_app", user_id=run_id)
    
    max_retries = 3
    current_attempt = 1
    
    # Initial trigger message
    msg_text = f"New Incident: {incident_desc}"
    
    while current_attempt <= max_retries:
        AgentLogger().emit_event("System", f"Attempt {current_attempt}", f"Starting attempt {current_attempt} of {max_retries}")
        
        # We must clear the agent states in the session to ensure the SequentialAgent and its sub-agents run again
        session = await runner.session_service.get_session(app_name="coordinator_app", user_id=run_id, session_id=session.id)
        if "_adk_agent_states" in session.state:
            del session.state["_adk_agent_states"]
        if "_adk_end_of_agents" in session.state:
            del session.state["_adk_end_of_agents"]
        
        # Run Coordinator Flow
        AgentLogger().emit_event("Coordinator", "Delegating", "Running Parallel Reroute and Signal-Timing Agents...")
        plan_output = ""
        user_msg = types.Content(role="user", parts=[types.Part.from_text(text=msg_text)])
        
        async for event in runner.run_async(user_id=run_id, session_id=session.id, new_message=user_msg):
            if hasattr(event, "model_response") and getattr(event, "model_response", None) and getattr(event.model_response, "usage_metadata", None):
                md = event.model_response.usage_metadata
                AgentLogger().log_call(event.author, getattr(md, "prompt_token_count", 0) or 0, getattr(md, "candidates_token_count", 0) or 0)
            
            if event.content and event.author == "coordinator_llm":
                if event.content.parts and event.content.parts[0].text:
                    plan_output += event.content.parts[0].text
                    AgentLogger().emit_event("Coordinator", "Merging", event.content.parts[0].text)
        
        AgentLogger().emit_event("Coordinator", "Merged Plan Completed", plan_output)
        
        # Run Verifier
        AgentLogger().emit_event("Verifier", "Evaluating", "Running safety checks on the proposed plan...")
        # Since the verifier is a single_turn agent, we can run it isolated using a new Runner and Session to avoid polluting history
        # Or we can run it in the same session, but the output schema returns JSON.
        verifier_runner = Runner(
            app_name="verifier_app",
            agent=verifier_agent,
            session_service=InMemorySessionService()
        )
        v_session = await verifier_runner.session_service.create_session(app_name="verifier_app", user_id=run_id)
        
        verifier_input = types.Content(role="user", parts=[types.Part.from_text(text=f"Incident: {incident_desc}\n\nProposed Plan:\n{plan_output}")])
        
        v_output = ""
        async for event in verifier_runner.run_async(user_id=run_id, session_id=v_session.id, new_message=verifier_input):
            if hasattr(event, "model_response") and getattr(event, "model_response", None) and getattr(event.model_response, "usage_metadata", None):
                md = event.model_response.usage_metadata
                AgentLogger().log_call(event.author, getattr(md, "prompt_token_count", 0) or 0, getattr(md, "candidates_token_count", 0) or 0)
            
            if event.content and event.author == "verifier_agent":
                if event.content.parts and event.content.parts[0].text:
                    v_output += event.content.parts[0].text
                
        AgentLogger().emit_event("Verifier", "Raw Output Received", v_output)
        
        try:
            # ADK single_turn with output_schema guarantees JSON string
            v_json = json.loads(v_output)
            decision = v_json.get("decision")
            reason = v_json.get("reason")
            constraint = v_json.get("constraint")
        except json.JSONDecodeError:
            AgentLogger().emit_event("System", "Error", "Failed to parse Verifier output as JSON.")
            decision = "REJECT"
            reason = "Failed to parse JSON"
            constraint = "Return valid JSON"
            
        AgentLogger().emit_event("Verifier", f"Decision: {decision}", f"Reason: {reason} | Constraint: {constraint}")
            
        if decision == "APPROVE":
            AgentLogger().emit_event("System", "Success", "Final Plan Approved!")
            break
        else:
            AgentLogger().emit_event("System", "Retry Triggered", "Plan Rejected. Retrying...")
            msg_text = f"The previous plan was REJECTED by the verifier.\nReason: {reason}\nCONSTRAINT FOR NEXT ITERATION: {constraint}\nCRITICAL: You MUST explicitly output a revised rerouting and signal timing plan that STRICTLY follows this constraint. Do NOT provide ambiguous advice or suspend routes without concrete detours. Specify exact alternative routes."
            current_attempt += 1
            
    if current_attempt > max_retries:
        AgentLogger().emit_event("System", "Timeout", "Exceeded maximum retries. Proceeding with last available plan.")

    AgentLogger().print_total()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python agent.py <incident_description>")
        sys.exit(1)
    incident_desc = sys.argv[1]
    await run_incident_response(incident_desc)

if __name__ == "__main__":
    asyncio.run(main())
