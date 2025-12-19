import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

# Tools Imports
from backend.tools.flight_tool import FlightSearchTool
from backend.tools.hotel_tool import HotelRecommendationTool
from backend.tools.places_tool import PlacesDiscoveryTool
from backend.tools.weather_tool import WeatherLookupTool
from backend.tools.budget_tool import BudgetEstimationTool

load_dotenv()

# --- 1. OUTPUT SCHEMA ---
class ItineraryOutput(BaseModel):
    trip_summary: str = Field(description="Summary of the trip.")
    flight_selected: dict = Field(description="Flight details.")
    hotel_selected: dict = Field(description="Hotel details.")
    total_budget_estimated: int = Field(description="Total cost in INR.")
    reasoning: str = Field(description="Why this flight/hotel was chosen.")
    day_wise_plan: list[dict] = Field(description="List of days with 'day' (number) and 'activity' (long description).")

# --- 2. INITIALIZE (Just setup LLM) ---
def initialize_travel_agent():
    if not os.getenv("GROQ_API_KEY"): raise ValueError("GROQ_API_KEY missing.")
    
    # Fast Model
    llm = ChatGroq(
        temperature=0.3,
        model_name="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY")
    )
    return llm

# --- 3. TURBO RUN FUNCTION (Manual Tool Calling) ---
def run_travel_agent(source, destination, days, budget, llm):
    print(f"🚀 STARTING TURBO MODE: {source} -> {destination}")

    # A. Execute Tools Manually (Python is faster than AI thinking)
    try:
        # 1. Flights
        flight_tool = FlightSearchTool()
        flight_data = flight_tool.run(f"{source} to {destination}")
        
        # 2. Hotels
        hotel_tool = HotelRecommendationTool()
        hotel_data = hotel_tool.run(destination)
        
        # 3. Weather
        weather_tool = WeatherLookupTool()
        weather_data = weather_tool.run(destination)
        
        # 4. Places
        places_tool = PlacesDiscoveryTool()
        places_data = places_tool.run(destination)

        print("✅ Data Fetched from Tools!")

    except Exception as e:
        print(f"⚠️ Tool Error: {e}")
        flight_data = "Check Online"
        hotel_data = "Standard Hotel"
        weather_data = "Sunny"
        places_data = "Famous Tourist Spots"

    # B. AI Formatting (Just one call)
    system_msg = """You are a Smart Travel Planner.
    I have already fetched the raw data for you. 
    YOUR JOB: Convert this raw data into a beautiful JSON itinerary.

    RAW DATA:
    - Flight Options: {flight_data}
    - Hotel Options: {hotel_data}
    - Weather: {weather_data}
    - Top Places: {places_data}
    - Trip Duration: {days} days
    - Budget Level: {budget}

    INSTRUCTIONS:
    1. Select the best flight and hotel from the data provided.
    2. Create a day-by-day plan using the 'Top Places'.
    3. Calculate total budget (Flight + Hotel + 3000 food/travel per day).
    4. OUTPUT MUST BE PURE JSON. NO TEXT.

    JSON SCHEMA:
    {{
      "trip_summary": "Short summary string",
      "flight_selected": {{ "airline": "Name", "price": 0 }},
      "hotel_selected": {{ "hotel_name": "Name", "price": 0 }},
      "total_budget_estimated": 0,
      "reasoning": "One sentence on why selected.",
      "day_wise_plan": [
        {{ "day": 1, "activity": "Detailed activity..." }}
      ]
    }}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", "Generate plan now.")
    ])

    # C. Run AI
    chain = prompt | llm
    
    response = chain.invoke({
        "flight_data": flight_data,
        "hotel_data": hotel_data,
        "weather_data": weather_data,
        "places_data": places_data,
        "days": days,
        "budget": budget
    })

    return response.content
