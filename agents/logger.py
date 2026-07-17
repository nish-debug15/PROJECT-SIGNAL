import asyncio
import json

class AgentLogger:
    _instance = None
    _total_prompt_tokens = 0
    _total_candidate_tokens = 0
    _subscribers = set()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentLogger, cls).__new__(cls)
            cls._instance._subscribers = set()
        return cls._instance

    def log_call(self, agent_name: str, prompt_tokens: int, candidate_tokens: int):
        self._total_prompt_tokens += prompt_tokens
        self._total_candidate_tokens += candidate_tokens
        
        # Gemini 2.5 Flash pricing (approx $0.075 / 1M in, $0.30 / 1M out)
        cost_input = (prompt_tokens / 1_000_000) * 0.075
        cost_output = (candidate_tokens / 1_000_000) * 0.30
        call_cost = cost_input + cost_output
        
        print(f"[{agent_name}] Tokens: {prompt_tokens} in / {candidate_tokens} out | Cost: ${call_cost:.6f}")

    def print_total(self):
        cost_input = (self._total_prompt_tokens / 1_000_000) * 0.075
        cost_output = (self._total_candidate_tokens / 1_000_000) * 0.30
        total_cost = cost_input + cost_output
        print(f"\n--- RUNNING TOTAL ---")
        print(f"Total Tokens: {self._total_prompt_tokens} in / {self._total_candidate_tokens} out")
        print(f"Total Cost: ${total_cost:.6f}")
        print(f"---------------------\n")

    def subscribe(self, queue: asyncio.Queue):
        self._subscribers.add(queue)

    def unsubscribe(self, queue: asyncio.Queue):
        self._subscribers.discard(queue)

    def emit_event(self, agent: str, action: str, data: str = "", status: str = "IN_PROGRESS"):
        event = {
            "agent": agent,
            "action": action,
            "data": data,
            "status": status
        }
        # Print to console for debugging
        if data:
            print(f"[{agent}] {action}: {data[:100]}...")
        else:
            print(f"[{agent}] {action}")
            
        # Broadcast to all websocket subscribers
        for queue in list(self._subscribers):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                pass
