import asyncio
import httpx
import websockets
import json
import sys

API_URL = "http://localhost:8080/api/incident"
WS_URL = "ws://localhost:8080/ws/logs"

INCIDENTS = [
    "Traffic signal failure at MG Road junction causing gridlock.",
    "Heavy rainfall resulting in severe flooding on Hebbal flyover.",
    "VIP movement blocking all lanes near Vidhana Soudha."
]

async def listen_for_incident_completion(incident_idx: int):
    async with websockets.connect(WS_URL) as ws:
        print(f"\n======================================")
        print(f"RUNNING TEST {incident_idx + 1}: {INCIDENTS[incident_idx]}")
        print(f"======================================")
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(API_URL, json={"incident_desc": INCIDENTS[incident_idx]})
            if resp.status_code != 200:
                print(f"Failed to trigger: {resp.text}")
                return

        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)
                
                agent = data.get("agent", "UNKNOWN")
                action = data.get("action", "")
                details = data.get("data", "")
                
                # Format output nicely
                if details:
                    print(f"[{agent}] {action}: {details}")
                else:
                    print(f"[{agent}] {action}")
                    
                if action == "Success" or action == "Timeout":
                    print(f"\n>>> TEST {incident_idx + 1} COMPLETE <<<\n")
                    break
                    
            except Exception as e:
                print(f"WS Error: {e}")
                break

async def main():
    for i in range(len(INCIDENTS)):
        await listen_for_incident_completion(i)
        await asyncio.sleep(2) # Give backend a moment before next run

if __name__ == "__main__":
    asyncio.run(main())
