import requests
import json
from langchain.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field

# शहरों के Latitude/Longitude (Open-Meteo को इसकी जरूरत होती है)
CITY_COORDS = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Goa": {"lat": 15.2993, "lon": 74.1240},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Bangalore": {"lat": 12.9716, "lon": 77.5946}
}

class WeatherInput(BaseModel):
    city: str = Field(..., description="City name to check weather for.")

class WeatherLookupTool(BaseTool):
    name: str = "Weather_Lookup_Tool"
    description: str = "Fetches real-time weather forecast using Open-Meteo API."
    args_schema: type[BaseModel] = WeatherInput

    def _run(self, city: str):
        # 1. निर्देशांक (Coordinates) प्राप्त करें
        coords = next((v for k, v in CITY_COORDS.items() if k.lower() in city.lower()), None)
        
        if not coords:
            return json.dumps({"error": f"Coordinates not found for {city}. Using mock data."})

        try:
            # 2. Open-Meteo API Call (Free, No Key Required)
            url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&daily=temperature_2m_max,weather_code&timezone=auto"
            response = requests.get(url)
            data = response.json()
            
            # 3. डेटा को सरल बनाएं
            daily = data.get("daily", {})
            temps = daily.get("temperature_2m_max", [])[:3] # अगले 3 दिन
            codes = daily.get("weather_code", [])[:3]
            
            # WMO Codes decoding
            weather_desc = {0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast", 45: "Fog", 61: "Rain"}
            
            forecast = []
            for i in range(len(temps)):
                desc = weather_desc.get(codes[i], "Variable")
                forecast.append(f"Day {i+1}: {desc} ({temps[i]}°C)")
                
            return json.dumps({"city": city, "forecast": forecast})
            
        except Exception as e:
            return json.dumps({"error": f"API Error: {str(e)}"})