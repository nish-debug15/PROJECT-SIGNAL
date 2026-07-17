from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from pydantic import BaseModel
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.coordinator.agent import run_incident_response
from agents.logger import AgentLogger

app = FastAPI(title="SIGNAL ADK API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IncidentRequest(BaseModel):
    incident_desc: str

@app.post("/api/incident")
async def trigger_incident(req: IncidentRequest):
    # Run the coordinator flow as a background task
    asyncio.create_task(run_incident_response(req.incident_desc))
    return {"status": "started", "message": "Incident response triggered."}

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    queue = asyncio.Queue()
    AgentLogger().subscribe(queue)
    try:
        while True:
            event = await queue.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        AgentLogger().unsubscribe(queue)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
