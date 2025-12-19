import sys, os, uvicorn, json
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.agent.travel_agent import initialize_travel_agent, run_travel_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_instance = initialize_travel_agent()

class TripRequest(BaseModel):
    source: str; destination: str; days: int; budget: str

@app.api_route("/", methods=["GET", "HEAD"])
async def home():
    return {"status": "Online", "message": "API is Live"}

@app.post("/generate_plan")
async def generate_plan(request: TripRequest):
    if not llm_instance:
        raise HTTPException(status_code=500, detail="AI Key Missing")
    try:
        raw_res = run_travel_agent(request.source, request.destination, request.days, request.budget, llm_instance)
        # Clean JSON
        clean = raw_res.replace("```json", "").replace("```", "").strip()
        start, end = clean.find('{'), clean.rfind('}') + 1
        return json.loads(clean[start:end])
    except Exception as e:
        print(f"Server Error: {e}")
        return {"trip_summary": "Error", "total_budget_estimated": 0, "day_wise_plan": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
