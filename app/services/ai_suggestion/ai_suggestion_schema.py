from pydantic import BaseModel

class ai_suggestion_request (BaseModel):
    destination:str
    amenities:str
    activities:str
    pacing:str
    food:str
    special_note:str
    
class ai_suggestion_response (BaseModel):
    response:str