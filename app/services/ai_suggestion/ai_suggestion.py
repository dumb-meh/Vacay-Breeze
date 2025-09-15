import os
import json
import openai
from uuid import uuid4
from dotenv import load_dotenv
from .ai_suggestion_schema import ai_suggestion_response, ai_suggestion_request, ItineraryData
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
        raw_response = self.get_openai_response(prompt, data)
        print(raw_response)

        try:
            parsed_data = json.loads(raw_response)  # GPT must return valid JSON
        except json.JSONDecodeError:
            raise ValueError("Failed to parse GPT response as JSON")

        itinerary_data = ItineraryData(
            itinerary_id=str(uuid4()),
            status=parsed_data.get("status", "complete"),
            days=parsed_data["days"]
        )

        return ai_suggestion_response(
            success=True,
            message="Itinerary generated successfully.",
            data=itinerary_data
        )

    
    def create_prompt(self, input_data: ai_suggestion_request) -> str:
        return f"""You are an expert travel planner specializing in creating detailed, personalized travel itineraries.

    Given the traveler's preferences below, generate a structured itinerary in **valid JSON format only**.

    ---

    **TRAVEL DETAILS**
    - Travelers: {input_data.total_adults} adults, {input_data.total_children} children (under 12)
    - Destination: {input_data.destination}
    - Departure City: {input_data.location}
    - Departure Date: {input_data.departure_date}
    - Return Date: {input_data.return_date}
    - Trip Duration: {self.calculate_trip_days()} days

    **ACCOMMODATION & AMENITIES**
    - Amenities Required: {', '.join(input_data.amenities)}

    **ACTIVITY PREFERENCES**
    - Preferred Activities: {', '.join(input_data.activities)}

    **VACATION PACE**
    - {', '.join(input_data.pacing)}

    **FOOD PREFERENCES**
    - Cuisine/Experience: {', '.join(input_data.food)}

    **SPECIAL REQUIREMENTS**
    - {input_data.special_notes if input_data.special_notes else 'None'}

    ---

    **OUTPUT INSTRUCTIONS**
    - Output must be valid JSON. Do not use markdown formatting, explanations, or natural language outside of the JSON.
    - Each day's entry must include:
        - `day_number`: integer
        - `date`: in YYYY-MM-DD format
        - `activities`: a list of structured activities
    - Each activity must include:
        - `id`: a unique string (e.g., UUID or number)
        - `time`: e.g., "9:00 AM"
        - `title`: short descriptive title
        - `description`: 1–2 sentence summary
        - `place`: name of place
        - `keyword`: one of ["Travel", "Meal", "Relaxation", "Cultural", "Outdoor", "Backup", "Leisure", "Historical", "Beach", "Museum", "Shopping", etc.]

    ---

    **EXAMPLE OUTPUT FORMAT** (structure only):

    {{
    "status": "complete",
    "days": [
        {{
        "day_number": 1,
        "date": "{input_data.departure_date}",
        "activities": [
            {{
            "id": "1",
            "time": "9:00 AM",
            "title": "Flight to Barcelona",
            "description": "Depart from {input_data.location} to {input_data.destination}. Ensure wheelchair assistance is arranged.",
            "place": "{input_data.location} Airport",
            "keyword": "Travel"
            }},
            {{
            "id": "2",
            "time": "12:00 PM",
            "title": "Hotel Check-in",
            "description": "Check in to a wheelchair-accessible hotel with amenities like pool, gym, and balcony.",
            "place": "Example Hotel Name",
            "keyword": "Relaxation"
            }}
        ]
        }}
    ]
    }}

    Start from Day 1 (departure date: {input_data.departure_date}) and continue through Day {self.calculate_trip_days()} (return date: {input_data.return_date}).
    Ensure each day has a mix of rest, food, and cultural activities, while considering children and accessibility needs.
    """



                        
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