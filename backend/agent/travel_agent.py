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
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ ERROR: GROQ_API_KEY is missing!")
        return None
    
    return ChatGroq(
        temperature=0.1, # Low temperature for factual consistency
        model_name="llama-3.1-8b-instant",
        api_key=api_key
    )

def run_travel_agent(source, destination, days, budget, llm):
    # --- 1. Fetch Real Data from Tools ---
    try:
        # We use .run() to get the string result from tools
        f_data = FlightSearchTool().run(f"{source} to {destination}")
        h_data = HotelRecommendationTool().run(destination)
        w_data = WeatherLookupTool().run(destination)
        p_data = PlacesDiscoveryTool().run(destination)
    except Exception as e:
        print(f"⚠️ Tool Fetch Error: {e}")
        f_data, h_data, w_data, p_data = "IndiGo/Air India", "Luxury Resort", "Sunny", "Local Attractions"

    # --- 2. Strict Prompt to force JSON Mapping ---
    system_msg = """You are a Travel Planner API. You MUST output ONLY valid JSON.
    
    TASK: Use the provided data to create a trip.
    
    DATA PROVIDED:
    - Origin: {source} | Destination: {destination}
    - Raw Flight Info: {f}
    - Raw Hotel Info: {h}
    - Weather Info: {w}
    - Places to visit: {p}
    - Budget Level: {b} | Days: {d}

    RULES:
    1. 'flight_selected': Extract the AIRLINE NAME and PRICE from the flight info. If missing, use 'IndiGo' and 5500.
    2. 'hotel_selected': Extract the HOTEL NAME and PRICE from the hotel info. If missing, use a famous hotel in {destination}.
    3. 'total_budget_estimated': Calculate (Flight + Hotel + 3000 per day for food). Output as a NUMBER.
    4. 'day_wise_plan': Create a detailed plan for {d} days using the provided 'Places'.
    5. NO CONVERSATION. NO MARKDOWN. JUST RAW JSON.

    JSON FORMAT:
    {{
      "trip_summary": "A {b} trip to {destination}.",
      "flight_selected": {{ "airline": "Airline Name", "price": 5000 }},
      "hotel_selected": {{ "hotel_name": "Hotel Name", "price": 4000 }},
      "total_budget_estimated": 25000,
      "reasoning": "Selected best value flight and hotel based on {b} budget.",
      "day_wise_plan": [ {{ "day": 1, "activity": "Arrive at {destination}..." }} ]
    }}"""

    prompt = ChatPromptTemplate.from_messages([("system", system_msg), ("human", "Generate the JSON now.")])
    chain = prompt | llm
    
    response = chain.invoke({
        "source": source, "destination": destination, "f": f_data, 
        "h": h_data, "w": w_data, "p": p_data, "d": days, "b": budget
    })
    
    return response.content
