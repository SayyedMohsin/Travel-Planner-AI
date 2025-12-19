import sys
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import re  # New Import for Cleaning

# Path Fix
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.agent.travel_agent import initialize_travel_agent, run_travel_agent
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    sys.exit(1)

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init Agent
print("⏳ Loading AI Model...")
agent_executor = None
try:
    agent_executor = initialize_travel_agent()
    print("✅ AI AGENT READY!")
except Exception as e:
    print(f"❌ Agent Init Error: {e}")

class TripRequest(BaseModel):
    source: str
    destination: str
    days: int
    budget: str

# Health Check
@app.get("/")
def home():
    return {"status": "Online", "message": "Backend is Running!"}

@app.post("/generate_plan")
def generate_plan(request: TripRequest):
    if not agent_executor:
        raise HTTPException(status_code=500, detail="AI Agent not loaded.")

    query = f"Plan a {request.days}-day trip from {request.source} to {request.destination}. Budget: {request.budget}. detailed Indian itinerary."
    
    try:
        response = run_travel_agent(query, agent_executor)
        
        # --- 🔥 ULTIMATE JSON CLEANING LOGIC ---
        if isinstance(response, str):
            # 1. Remove Markdown Code Blocks
            clean = response.replace("```json", "").replace("```", "").strip()
            
            # 2. Remove "Final Answer:" text if present
            if "Final Answer:" in clean:
                clean = clean.split("Final Answer:")[-1].strip()

            # 3. Find the FIRST '{' and the LAST '}' 
            # (This removes any extra text before or after the JSON)
            start_idx = clean.find('{')
            end_idx = clean.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                clean = clean[start_idx:end_idx]
            
            # 4. Try Loading
            try:
                return json.loads(clean)
            except json.JSONDecodeError as je:
                print(f"JSON Parse Error: {je}")
                # Fallback if AI creates bad JSON
                raise HTTPException(status_code=500, detail="AI returned invalid JSON format.")
                
        return response

    except Exception as e:
        print(f"❌ Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
