import json
import random
from langchain.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field

class HotelInput(BaseModel):
    city: str = Field(..., description="The destination city.")
    preference: str = Field("Any", description="Preference: 'Budget', 'Luxury', or 'Any'.")

class HotelRecommendationTool(BaseTool):
    name: str = "Hotel_Recommendation_Tool"
    description: str = "Finds hotels in a city."
    args_schema: type[BaseModel] = HotelInput

    def _run(self, city: str, preference: str):
        # 1. Names Database
        prefixes = ["Grand", "Royal", "City", "Lemon", "Taj", "Oberoi", "Ginger", "Treebo"]
        suffixes = ["Palace", "Resort", "Inn", "Suites", "Plaza", "Stay", "Residency"]
        
        # 2. Generate Name based on city
        if preference.lower() == "luxury":
            hotel_name = f"The {city} {random.choice(['Palace', 'Grand', 'Oberoi', 'Marriott'])}"
            price = random.randint(8000, 15000)
            rating = 5.0
        else:
            hotel_name = f"{random.choice(prefixes)} {city} {random.choice(suffixes)}"
            price = random.randint(1500, 4000)
            rating = round(random.uniform(3.5, 4.5), 1)

        # 3. Return Data
        hotel_data = {
            "hotel_name": hotel_name,
            "city": city,
            "price": price,
            "rating": rating,
            "address": f"Near City Center, {city}"
        }
        
        return json.dumps(hotel_data)