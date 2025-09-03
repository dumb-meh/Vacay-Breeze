from pydantic import BaseModel

class ai_suggestion_request (BaseModel):
    total_adults:str
    total_children:str
    destination:str
    location:str
    departure_date:str
    return_date:str
    amenities:str
    activities:str
    pacing:str
    food:str
    special_notes:str
    
class ai_suggestion_response (BaseModel):
    response:str