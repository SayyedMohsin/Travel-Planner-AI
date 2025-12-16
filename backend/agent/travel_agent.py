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

    # --- SWITCHING BACK TO SMART MODEL (STABLE) ---
    llm = ChatGroq(
        temperature=0.2, 
        model_name="llama-3.3-70b-versatile", # यह मॉडल कभी गलती नहीं करता
        api_key=os.getenv("GROQ_API_KEY")
    )

    schema_json = ItineraryOutput.schema_json(indent=2)
    
    system_msg = """You are an elite Travel Architect for India.
    
    YOUR GOAL: Create a highly detailed, day-by-day travel story.
    
    CRITICAL RULES:
    1. **Descriptions:** Write a short paragraph for each day describing morning, afternoon, and night. Mention specific Indian dishes.
    2. **Reliability:** Ensure all JSON fields are filled correctly.
    3. **JSON Only:** Your final output must be pure JSON matching the schema below.
    
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
        
        # Clean JSON Logic
        if "```json" in output: 
            output = output.split("```json")[1].split("```")[0].strip()
        elif "```" in output: 
            output = output.split("```")[1].split("```")[0].strip()
            
        return output
    except Exception as e:
        print(f"❌ Agent Error: {e}")
        # Return Error JSON with explicit message
        return json.dumps({
            "trip_summary": "System faced an error generating the plan.",
            "flight_selected": {"airline": "Standard Air", "price": 5000},
            "hotel_selected": {"hotel_name": "City Hotel", "price": 3000},
            "total_budget_estimated": 0, # Frontend will detect this
            "reasoning": f"Internal Error: {str(e)}",
            "day_wise_plan": []
        })