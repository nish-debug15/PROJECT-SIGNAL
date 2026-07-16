import asyncio
from typing import AsyncGenerator
from google.genai import types
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
import json

class MockLlm(BaseLlm):
    model: str = "mock-llm"

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        
        prompt = ""
        for content in llm_request.contents:
            if content.parts:
                for part in content.parts:
                    if part.text:
                        prompt += part.text + "\n"
            
        full_lower = prompt.lower()

        if "proposed plan:" in full_lower:
            # Verifier
            if "outer ring road" in full_lower:
                response_text = json.dumps({"decision": "APPROVE", "reason": "Looks good", "constraint": ""})
            else:
                response_text = json.dumps({
                    "decision": "REJECT",
                    "reason": "Route goes through Silk Board which is heavily flooded.",
                    "constraint": "Avoid Silk Board entirely. Reroute via Outer Ring Road."
                })
        elif "[reroute_agent] said:" in full_lower:
            # Coordinator
            if "outer ring road" in full_lower:
                response_text = "FINAL MERGED PLAN: Reroute via Outer Ring Road."
            else:
                response_text = "INITIAL PLAN: Route via Silk Board."
        else:
            # Reroute / Signal
            if "rejected by the verifier" in full_lower:
                response_text = "MERGED RETRY PLAN: Reroute via Outer Ring Road."
            else:
                response_text = "INITIAL PLAN: Route via Silk Board."

        await asyncio.sleep(0.01)
        
        yield LlmResponse(
            partial=False,
            content=types.Content(role="model", parts=[types.Part.from_text(text=response_text)])
        )
