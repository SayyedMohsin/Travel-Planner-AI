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

    # --- USING FAST MODEL ---
    llm = ChatGroq(
        temperature=0.1,  # Temperature kam kiya taaki AI creative na ho, bas kaam kare
        model_name="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY")
    )

    schema_json = ItineraryOutput.schema_json(indent=2)
    
    # --- STRICT SYSTEM PROMPT ---
    system_msg = """You are a JSON-only API. You are NOT a chatbot.
    
    YOUR TASK: Plan a detailed trip based on user input.
    
    CRITICAL INSTRUCTIONS:
    1. **OUTPUT FORMAT:** You must output ONLY a valid JSON object.
    2. **NO TEXT:** Do NOT write "Here is the plan" or "Note:". Do NOT use markdown code blocks like ```json. Just raw JSON.
    3. **CONTENT:**
       - 'day_wise_plan': Write 3-4 sentences for each day. Mention real places and food.
       - 'flight_selected': Must include 'airline' and 'price'.
       - 'hotel_selected': Must include 'hotel_name' and 'price'.
       - 'total_budget_estimated': Must be a number (Integer).
    
    SCHEMA TO FOLLOW:
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
        
        # Cleaning Logic (Agar AI ne fir bhi galti ki)
        if "```json" in output: 
            output = output.split("```json")[1].split("```")[0].strip()
        elif "```" in output: 
            output = output.split("```")[1].split("```")[0].strip()
            
        return output
    except Exception as e:
        print(f"❌ Agent Error: {e}")
        # Fallback JSON
        return json.dumps({
            "trip_summary": "Error generating plan.",
            "flight_selected": {"airline": "Standard Air", "price": 5000},
            "hotel_selected": {"hotel_name": "City Hotel", "price": 3000},
            "total_budget_estimated": 0,
            "reasoning": "AI Format Error. Please try again.",
            "day_wise_plan": []
        })
