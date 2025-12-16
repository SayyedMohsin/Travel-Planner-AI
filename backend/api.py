import sys
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

# Path Fix
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.agent.travel_agent import initialize_travel_agent, run_travel_agent
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    sys.exit(1)

app = FastAPI()

# --- CORS (Connection Open) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init Agent
print("⏳ Loading Fast AI Model...")
agent_executor = None
try:
    agent_executor = initialize_travel_agent()
    print("✅ FAST AI AGENT READY!")
except Exception as e:
    print(f"❌ Agent Init Error: {e}")

class TripRequest(BaseModel):
    source: str
    destination: str
    days: int
    budget: str

@app.post("/generate_plan")
def generate_plan(request: TripRequest):
    if not agent_executor:
        raise HTTPException(status_code=500, detail="AI Agent not loaded.")

    query = f"Plan a {request.days}-day trip from {request.source} to {request.destination}. Budget: {request.budget}. detailed Indian itinerary."
    
    try:
        response = run_travel_agent(query, agent_executor)
        if isinstance(response, str):
            clean = response.replace("```json", "").replace("```", "").strip()
            if "Final Answer:" in clean: clean = clean.split("Final Answer:")[-1].strip()
            return json.loads(clean)
        return response
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Host 0.0.0.0 is safest for connections
    uvicorn.run(app, host="0.0.0.0", port=8000)