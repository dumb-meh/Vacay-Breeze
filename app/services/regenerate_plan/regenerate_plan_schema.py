from pydantic import BaseModel
from typing import Dict,List
class regenerate_plan_request(BaseModel):
    current_itinerary: Dict[str, str]
    user_change: str
    day_plan:List[Dict[str, str]]
    place:str
    user_info: Dict[str, str]
    
class regenerate_plan_response(BaseModel):
    updated_plan: str  