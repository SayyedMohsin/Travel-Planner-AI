import sys
import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request
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

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init Agent (Now it just loads LLM)
print("⏳ Loading AI Model...")
llm_instance = None
try:
    llm_instance = initialize_travel_agent()
    print("✅ AI AGENT READY!")
except Exception as e:
    print(f"❌ Agent Init Error: {e}")

class TripRequest(BaseModel):
    source: str
    destination: str
    days: int
    budget: str

@app.api_route("/", methods=["GET", "HEAD"])
async def home(request: Request):
    return {"status": "Online", "message": "Backend is Running!"}

@app.post("/generate_plan")
def generate_plan(request: TripRequest):
    if not llm_instance:
        raise HTTPException(status_code=500, detail="AI Model not loaded.")

    print(f"📨 New Request: {request.destination} for {request.days} days")

    try:
        # --- CALL NEW TURBO FUNCTION ---
        # Note: We pass raw data now, not a string query
        response = run_travel_agent(
            request.source, 
            request.destination, 
            request.days, 
            request.budget, 
            llm_instance
        )
        
        # --- CLEANING LOGIC ---
        if isinstance(response, str):
            clean = response.replace("```json", "").replace("```", "").strip()
            if "Final Answer:" in clean: clean = clean.split("Final Answer:")[-1].strip()
            
            # Find JSON Brackets
            start = clean.find('{')
            end = clean.rfind('}') + 1
            if start != -1 and end != 0:
                clean = clean[start:end]
            
            try:
                data = json.loads(clean)
                print("✅ JSON Generated Successfully")
                return data
            except json.JSONDecodeError:
                print("⚠️ JSON Parse Failed, sending Fallback.")
                # Fallback only if JSON fails
                return {
                    "trip_summary": f"Trip to {request.destination}",
                    "flight_selected": {"airline": "Check Online", "price": 5000},
                    "hotel_selected": {"hotel_name": "Grand Hotel", "price": 4000},
                    "total_budget_estimated": 15000 * request.days,
                    "reasoning": "AI raw text response. JSON parsing failed.",
                    "day_wise_plan": [
                        {"day": 1, "activity": "Arrival and relaxation."},
                        {"day": 2, "activity": "City tour and sightseeing."}
                    ]
                }
                
        return response

    except Exception as e:
        print(f"❌ Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
