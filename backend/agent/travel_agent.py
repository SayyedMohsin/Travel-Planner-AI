import os
from dotenv import load_dotenv
import json

# --- IMPORTS ---
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_groq import ChatGroq 
from langchain.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

# Tools Imports
from backend.tools.flight_tool import FlightSearchTool
from backend.tools.hotel_tool import HotelRecommendationTool
from backend.tools.places_tool import PlacesDiscoveryTool
from backend.tools.weather_tool import WeatherLookupTool
from backend.tools.budget_tool import BudgetEstimationTool

load_dotenv()

# --- OUTPUT SCHEMA ---
class ItineraryOutput(BaseModel):
    trip_summary: str = Field(description="Summary of the trip.")
    flight_selected: dict = Field(description="Flight details.")
    hotel_selected: dict = Field(description="Hotel details.")
    total_budget_estimated: int = Field(description="Total cost in INR.")
    reasoning: str = Field(description="Why this flight/hotel was chosen.")
    day_wise_plan: list[dict] = Field(description="List of days with 'day' (number) and 'activity' (long description).")

def initialize_travel_agent():
    tools = [FlightSearchTool(), HotelRecommendationTool(), PlacesDiscoveryTool(), WeatherLookupTool(), BudgetEstimationTool()]
    
    if not os.getenv("GROQ_API_KEY"): raise ValueError("GROQ_API_KEY missing.")

    # --- FAST MODEL ---
    llm = ChatGroq(
        temperature=0.1, 
        model_name="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY")
    )

    schema_json = ItineraryOutput.schema_json(indent=2)
    
    # --- ONE-SHOT PROMPT (The Magic Fix) ---
    system_msg = """You are a smart Travel Assistant.
    
    YOUR GOAL: Generate a JSON plan. Do not talk. Do not explain. Just JSON.
    
    EXAMPLE OUTPUT (Follow this structure EXACTLY):
    {{
      "trip_summary": "A wonderful trip to Goa.",
      "flight_selected": {{ "airline": "IndiGo", "price": 5000 }},
      "hotel_selected": {{ "hotel_name": "Goa Beach Resort", "price": 4000 }},
      "total_budget_estimated": 20000,
      "reasoning": "Cheapest flight and best rated hotel selected.",
      "day_wise_plan": [
        {{ "day": 1, "activity": "Arrive in Goa, check into hotel, and visit Baga Beach." }},
        {{ "day": 2, "activity": "Visit Fort Aguada and enjoy water sports." }}
      ]
    }}

    NOW GENERATE FOR THE USER INPUT.
    SCHEMA:
    {schema}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    prompt = prompt.partial(schema=schema_json)
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

def run_travel_agent(query: str, agent_executor):
    print(f"--- Processing: {query} ---")
    try:
        result = agent_executor.invoke({"input": query})
        output = result['output']
        return output
    except Exception as e:
        print(f"❌ Agent Error: {e}")
        # --- EMERGENCY FALLBACK (Agar AI fail ho to ye dikhao) ---
        return json.dumps({
            "trip_summary": "Standard Trip Plan (AI Busy)",
            "flight_selected": {"airline": "Standard Airlines", "price": 4500},
            "hotel_selected": {"hotel_name": "Premium City Hotel", "price": 3500},
            "total_budget_estimated": 15000,
            "reasoning": "Selected based on standard market rates as AI was unresponsive.",
            "day_wise_plan": [
                {"day": 1, "activity": "Arrival at destination, check-in to hotel, and evening local market tour."},
                {"day": 2, "activity": "Full day sightseeing of famous city landmarks and cultural spots."},
                {"day": 3, "activity": "Morning relaxation and departure back home."}
            ]
        })
