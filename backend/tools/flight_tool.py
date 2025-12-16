import json
import random
from langchain.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field

class FlightSearchInput(BaseModel):
    source_city: str = Field(..., description="Departure city.")
    destination_city: str = Field(..., description="Destination city.")
    preference: str = Field("cheapest", description="Preference: 'cheapest' or 'fastest'.")

class FlightSearchTool(BaseTool):
    name: str = "Flight_Search_Tool"
    description: str = "Search for flights between cities."
    args_schema: type[BaseModel] = FlightSearchInput

    def _run(self, source_city: str, destination_city: str, preference: str):
        # 1. Airlines List
        airlines = ["IndiGo", "Air India", "Vistara", "SpiceJet", "Akasa Air"]
        
        # 2. Random Price Generator (Dynamic)
        base_price = 3000
        distance_factor = random.randint(1000, 5000)
        price = base_price + distance_factor
        
        if preference == "luxury" or preference == "fastest":
            price += 4000
            airline = "Vistara"
        else:
            airline = random.choice(airlines)

        # 3. Random Time
        dep_hour = random.randint(6, 20)
        dep_time = f"{dep_hour:02d}:30"
        duration = random.choice([1.5, 2.0, 2.5, 3.0])

        # 4. Construct Result (Always return data)
        flight_data = {
            "flight_id": f"{airline[:2].upper()}-{random.randint(100, 999)}",
            "source": source_city,
            "destination": destination_city,
            "airline": airline,
            "price": price,
            "departure": dep_time,
            "duration": f"{duration} hrs"
        }
        
        return json.dumps(flight_data)