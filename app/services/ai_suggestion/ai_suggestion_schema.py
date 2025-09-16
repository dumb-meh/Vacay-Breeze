from pydantic import BaseModel
from typing import List

class ai_suggestion_request (BaseModel):
    total_adults:int
    total_children:int
    destination:str
    location:str
    departure_date:str
    return_date:str
    amenities:List[str]
    activities:List[str]
    pacing:list[str]
    food:list[str]
    special_notes:str    
class Activity(BaseModel):
    id: str
    time: str
    title: str
    description: str
    place: str
    keyword: str
class Day(BaseModel):
    day_number: int
    date: str
    activities: List[Activity]
class ItineraryData(BaseModel):
    itinerary_id: str
    days: List[Day]
    status: str
class ai_suggestion_response(BaseModel):
    success: bool
    message: str
    data: ItineraryData
