import asyncio
import os
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm
from google.adk.models.llm_request import LlmRequest
from google.genai import types

load_dotenv()

async def main():
    llm = LiteLlm(model="gemini/gemini-2.5-flash", max_tokens=100)
    req = LlmRequest(contents=[types.Content(role="user", parts=[types.Part.from_text(text="Say hello")])])
    
    async for resp in llm.generate_content_async(req):
        print(f"Resp: {resp.content.parts[0].text if resp.content else 'None'}")
        if resp.usage_metadata:
            print(f"Usage: {resp.usage_metadata.prompt_token_count} in, {resp.usage_metadata.candidates_token_count} out")
        else:
            print("No usage_metadata in LlmResponse")

if __name__ == "__main__":
    asyncio.run(main())
