import os
import json
import openai
from dotenv import load_dotenv
from .regenerate_plan_schema import regenerate_plan_response, regenerate_plan_request

load_dotenv()

class RegeneratePlan:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def regenerate_plan(self, input_data: regenerate_plan_request) -> regenerate_plan_response:     
        prompt = self.create_prompt(input_data)
        response = self.get_openai_response(prompt, str(input_data.dict()))
        try:
            response_json = json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse OpenAI response as JSON: {e}")
        return regenerate_plan_response(**response_json)
    
    def create_prompt(self, input_data: regenerate_plan_request) -> str:
        return f"""You are an expert travel planner. A traveler is searching for NEW activity suggestions to add to their day.

    USER SEARCH QUERY:
    {input_data.user_search}

    CURRENT DAY PLAN:
    {input_data.day_plan}
    
    Itinerary ID: 
    {input_data.itinerary_id}

    USER TRAVEL INFO:
    {input_data.user_info}

    DESTINATION: {input_data.user_info.get("destination", "Unknown")}
    TRAVELERS: {input_data.user_info.get("total_adults", "N/A")} adults, {input_data.user_info.get("total_children", "N/A")} children

    INSTRUCTIONS:
    1. Use web search to find activities in {input_data.user_info.get("destination", "Unknown")} that match the user's search query
    2. Suggest ONLY NEW activities that are NOT already in their current day plan
    3. All suggestions must be real places/activities
    4. Consider group size when making suggestions
    5. Generate exactly 4 alternative options

    OUTPUT ONLY valid JSON exactly like this example:

    {{
    "success": true,
    "data": {{
        "itinerary_id": "{input_data.itinerary_id}",
        "alternative_options": [
        {{
            "option": 1,
            "id": "activity-day-1-6",
            "time": "9:30 AM",
            "title": "Disneyland Paris",
            "description": "Visit the magical Disneyland Paris theme park with attractions suitable for children of all ages. Wheelchair accessible rides available.",
            "place": "Disneyland Paris",
            "keyword": "entertainment"
        }},
        ...................
        ...................
        {{
            "option": 4,
            "id": "activity-day-1-9",
            "time": "2:00 PM",
            "title": "Seine River Cruise",
            "description": "Enjoy a relaxing boat cruise along the Seine River, taking in iconic sights like the Eiffel Tower and Notre-Dame Cathedral. Suitable for all ages.",
            "place": "Seine River",
            "keyword": "sightseeing"}}
    }},
    "message": "Alternative activities generated successfully"
    }}

    IMPORTANT: Use web search for real venues. Generate unique UUID for id. NO markdown, ONLY JSON."""


    
    def get_openai_response(self, prompt: str, data: str) -> str:
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": data}],
            temperature=0.7            
        )
        raw_content = completion.choices[0].message.content.strip()
        print(raw_content)
        return raw_content