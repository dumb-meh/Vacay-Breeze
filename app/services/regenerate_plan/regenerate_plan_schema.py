from pydantic import BaseModel
from typing import Dict,List,Any
class regenerate_plan_request(BaseModel):
    current_itinerary: Dict[str, str]
    user_change: str
    day_plan:List[Dict[str, str]]
    user_info: Dict[str, str]
    
class regenerate_plan_response(BaseModel):
    updated_itinerary: List[Dict[str, Any]]