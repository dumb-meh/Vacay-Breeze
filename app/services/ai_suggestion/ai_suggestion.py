import os
import json
import openai
from dotenv import load_dotenv
from .ai_suggestion_schema import ai_suggestion_response, ai_suggestion_request
import datetime

load_dotenv()
class AISuggestion:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def get_suggestion(self, input_data: ai_suggestion_request) -> ai_suggestion_response:
        self.departure_date = input_data.departure_date
        self.return_date = input_data.return_date
                     
        prompt = self.create_prompt(input_data)
        data = str(input_data.dict())
        response = self.get_openai_response(prompt, data)
        return ai_suggestion_response(response=response)
    
    def create_prompt(self, input_data: ai_suggestion_request) -> str:
        return f"""You are an expert travel planner specializing in creating detailed, personalized itineraries. Based on the provided travel preferences, create a comprehensive day-by-day travel plan.

                    TRAVEL DETAILS:
                    - Travelers: {input_data.total_adults} adults, {input_data.total_children} children (under 12)
                    - Destination: {input_data.destination}
                    - Current Location: {input_data.location}
                    - Departure Date: {input_data.departure_date}
                    - Return Date: {input_data.return_date}
                    - Trip Duration: {self.calculate_trip_days()} days

                    ACCOMMODATION PREFERENCES:
                    Amenities Required: {input_data.amenities}

                    ACTIVITY PREFERENCES:
                    Preferred Activities: {input_data.activities}

                    VACATION PACE:
                    {input_data.pacing}

                    DINING PREFERENCES:
                    Food Experience: {input_data.food}

                    SPECIAL REQUIREMENTS:
                    {input_data.special_notes if input_data.special_notes else 'None'}

                    INSTRUCTIONS:
                    1. Create a detailed day-by-day itinerary using a consistent structured format.
                    2. Each activity should include the time, title, description, and place.
                    3. Consider the vacation pace and group size (including children) when planning.
                    4. Incorporate preferred activities, amenities, and food experiences.
                    5. Include real establishments where possible (hotels, restaurants, attractions).
                    6. Include travel time between locations and allow downtime where needed.
                    7. Suggest indoor backup activities in case of bad weather.
                    9. STRICTLY FOLLOW THE FORMAT below — DO NOT use paragraphs or markdown.

                    OUTPUT FORMAT:

                    **Day 1 ({input_data.departure_date}):**
                    [
                    {{
                        "time": "9:00 AM",
                        "title": "Flight Departure",
                        "description": "Depart from {input_data.location} on a non-stop flight to {input_data.destination}. Ensure wheelchair assistance if needed.",
                        "place": "{input_data.location} Airport"
                    }},
                    {{
                        "time": "12:00 PM",
                        "title": "Hotel Check-in",
                        "description": "Check in at a hotel with required amenities (e.g., pool, outdoor space, parking).",
                        "place": "Example Hotel Name"
                    }},
                    {{
                        "time": "1:00 PM",
                        "title": "Lunch at Local Spot",
                        "description": "Enjoy a family-friendly lunch featuring {input_data.food.lower()}.",
                        "place": "Example Restaurant Name"
                    }}
                    ]

                    [Repeat this format through Day {self.calculate_trip_days()} ({input_data.return_date})] """


                        
    def get_openai_response(self, prompt: str, data: str) -> str:
        completion = self.client.chat.completions.create(
            model="gpt-4o-search-preview",
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": data}]      
        )
        return completion.choices[0].message.content
    
    def calculate_trip_days(self) -> int:
        departure = datetime.datetime.strptime(self.departure_date, '%Y-%m-%d')
        return_date = datetime.datetime.strptime(self.return_date, '%Y-%m-%d')
        return (return_date - departure).days + 1