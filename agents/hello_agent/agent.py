from google.adk.agents import Agent

root_agent = Agent(
    name="hello_agent",
    model="gemini-2.5-flash",
    description="A simple hello agent to verify ADK is working.",
    instruction="You are a friendly assistant. Greet the user and confirm that the SIGNAL project ADK setup is working correctly.",
)
