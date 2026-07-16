import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

root_agent = Agent(
    name="hello_agent",
    model=LiteLlm(
        model="openrouter/google/gemini-2.5-flash",
        max_tokens=4096,
    ),
    description="A simple hello agent to verify ADK is working.",
    instruction="You are a friendly assistant. Greet the user and confirm that the SIGNAL project ADK setup is working correctly.",
)
