import sys
import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import re

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

# --- 🔥 FIX: Allow both GET and HEAD requests ---
@app.api_route("/", methods=["GET", "HEAD"])
async def home(request: Request):
    return {"status": "Online", "message": "Backend is Running Live!"}

@app.post("/generate_plan")
def generate_plan(request: TripRequest):
    if not agent_executor:
        raise HTTPException(status_code=500, detail="AI Agent not loaded.")

    query = f"Plan a {request.days}-day trip from {request.source} to {request.destination}. Budget: {request.budget}. detailed Indian itinerary."
    
    try:
        response = run_travel_agent(query, agent_executor)
        
        # --- JSON CLEANING LOGIC ---
        if isinstance(response, str):
            # Clean Markdown
            clean = response.replace("```json", "").replace("```", "").strip()
            if "Final Answer:" in clean: clean = clean.split("Final Answer:")[-1].strip()

            # Find valid JSON boundaries
            start_idx = clean.find('{')
            end_idx = clean.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                clean = clean[start_idx:end_idx]
            
            try:
                return json.loads(clean)
            except json.JSONDecodeError:
                # Fallback if JSON is still bad
                print("⚠️ Invalid JSON from AI, returning fallback.")
                return {
                    "trip_summary": f"Trip to {request.destination}",
                    "flight_selected": {"airline": "Check Online", "price": 5000},
                    "hotel_selected": {"hotel_name": "Standard Hotel", "price": 3000},
                    "total_budget_estimated": 15000,
                    "reasoning": "AI generated text instead of JSON. Please try again.",
                    "day_wise_plan": []
                }
                
        return response

    except Exception as e:
        print(f"❌ Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
