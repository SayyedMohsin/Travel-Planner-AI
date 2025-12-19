import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Tools Imports
from backend.tools.flight_tool import FlightSearchTool
from backend.tools.hotel_tool import HotelRecommendationTool
from backend.tools.places_tool import PlacesDiscoveryTool
from backend.tools.weather_tool import WeatherLookupTool

load_dotenv()

def initialize_travel_agent():
    if not os.getenv("GROQ_API_KEY"):
        print("❌ ERROR: GROQ_API_KEY is missing from Environment Variables!")
        return None
    
    return ChatGroq(
        temperature=0.2,
        model_name="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY")
    )

def run_travel_agent(source, destination, days, budget, llm):
    # --- Execute Tools Manually (Super Fast) ---
    try:
        flight_data = FlightSearchTool()._run(f"{source} to {destination}")
        hotel_data = HotelRecommendationTool()._run(destination)
        weather_data = WeatherLookupTool()._run(destination)
        places_data = PlacesDiscoveryTool()._run(destination)
    except Exception as e:
        print(f"⚠️ Tool Error: {e}")
        flight_data, hotel_data, weather_data, places_data = "N/A", "N/A", "Cloudy", "Tourist Spots"

    system_msg = """You are a Smart Travel Planner. 
    Convert raw data into a PURE JSON itinerary. No conversational text.
    
    DATA:
    - Origin: {source}, Destination: {destination}
    - Flights: {f}, Hotels: {h}, Weather: {w}, Places: {p}
    - Duration: {d} days, Budget: {b}

    OUTPUT SCHEMA (Must be valid JSON):
    {{
      "trip_summary": "Summary text",
      "flight_selected": {{ "airline": "Name", "price": 5000 }},
      "hotel_selected": {{ "hotel_name": "Name", "price": 4000 }},
      "total_budget_estimated": 15000,
      "reasoning": "Quick logic",
      "day_wise_plan": [ {{ "day": 1, "activity": "desc" }} ]
    }}"""

    prompt = ChatPromptTemplate.from_messages([("system", system_msg), ("human", "Create JSON now.")])
    chain = prompt | llm
    
    response = chain.invoke({
        "source": source, "destination": destination, "f": flight_data, 
        "h": hotel_data, "w": weather_data, "p": places_data, "d": days, "b": budget
    })
    return response.content
