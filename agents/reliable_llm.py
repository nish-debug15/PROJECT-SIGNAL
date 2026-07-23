from typing import AsyncGenerator
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from agents.logger import AgentLogger

class ReliableLlm(BaseLlm):
    model: str = "reliable-llm"
    real_model: BaseLlm
    mock_model: BaseLlm
    agent_name: str

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        try:
            # Emit live mode status
            AgentLogger().emit_event("System", f"{self.agent_name} Mode", "LIVE")
            
            # Delegate to real model
            async for response in self.real_model.generate_content_async(llm_request, stream):
                yield response
                
        except Exception as e:
            # On exception (rate limit, API error, etc.), emit simulated fallback mode
            AgentLogger().emit_event("System", f"{self.agent_name} Mode", "SIMULATED (Fallback)")
            AgentLogger().emit_event("System", f"{self.agent_name} Error", str(e))
            
            # Fallback to MockLLM for this specific call
            async for response in self.mock_model.generate_content_async(llm_request, stream):
                yield response
