from pydantic import BaseModel
from typing import List, Union, Dict,Any  

class ai_suggestion_request (BaseModel):
    total_adults:int
    total_children:int
    destination:str
    destination_state:str
    location:str
    departure_date:str
    return_date:str
    amenities:List[str]
    activities:List[str]
    pacing:list[str]
    food:list[str]
    special_note:str    
class ai_suggestion_response(BaseModel):
    success: bool
    message: str
    data: Union[str, List[Dict], Dict[str, Any]]