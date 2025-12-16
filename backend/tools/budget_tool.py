import json
from langchain.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field

class BudgetInput(BaseModel):
    days: int = Field(..., description="Number of days.")
    category: str = Field(..., description="Budget category: 'Budget' or 'Luxury'.")

class BudgetEstimationTool(BaseTool):
    name: str = "Budget_Estimation_Tool"
    description: str = "Estimates total trip cost including food and local travel."
    args_schema: type[BaseModel] = BudgetInput

    def _run(self, days: int, category: str):
        try:
            # Base daily cost (Food + Travel)
            if category.lower() == "luxury":
                daily_cost = 5000
            else:
                daily_cost = 2000
                
            total_expenses = daily_cost * int(days)
            
            return json.dumps({
                "estimated_total_expenses": total_expenses, 
                "currency": "INR",
                "breakdown": f"{daily_cost}/day for {days} days"
            })
        except Exception as e:
            # Safe Fallback
            return json.dumps({
                "estimated_total_expenses": 5000 * int(days), 
                "currency": "INR",
                "error": str(e)
            })