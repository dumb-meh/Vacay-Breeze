from pydantic import BaseModel
class regenerate_plan_request(BaseModel):
    current_plan: str  
    user_change: str
    place:str
    
class regenerate_plan_response(BaseModel):
    updated_plan: str  