import json
from langchain.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field

PLACES_DB = {
    "Goa": ["Baga Beach", "Fort Aguada", "Dudhsagar Falls"],
    "Delhi": ["Red Fort", "India Gate", "Qutub Minar"]
}

class PlacesInput(BaseModel):
    city: str = Field(...)

class PlacesDiscoveryTool(BaseTool):
    name: str = "Places_Discovery_Tool"
    description: str = "Finds tourist places."
    args_schema: type[BaseModel] = PlacesInput

    def _run(self, city: str):
        places = next((v for k, v in PLACES_DB.items() if k.lower() in city.lower()), ["City Center", "Local Market"])
        return json.dumps({"places": places})