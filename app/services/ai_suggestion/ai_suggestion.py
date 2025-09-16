import os
import json
import openai
from uuid import uuid4
from dotenv import load_dotenv
import concurrent.futures
from .ai_suggestion_schema import ai_suggestion_response, ai_suggestion_request, ItineraryData
import datetime

load_dotenv()

class AISuggestion:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def get_suggestion(self, input_data: ai_suggestion_request) -> ai_suggestion_response:
        self.departure_date = input_data.departure_date
        self.return_date = input_data.return_date
        trip_days = self.calculate_trip_days()

        # Step 1: Get outline
        outline_prompt = self.create_outline_prompt(input_data, trip_days)
        raw_outline = self.get_openai_response(outline_prompt, str(input_data.dict()))
        outline_json = json.loads(self.clean_json(raw_outline))
        days_outline = outline_json.get("days", [])

        if not days_outline:
            raise ValueError("Outline failed or returned empty 'days'.")

        # Step 2: Split into chunks (e.g. 5-day)
        chunk_size = 5
        chunks = [days_outline[i:i + chunk_size] for i in range(0, len(days_outline), chunk_size)]

        detailed_days = []

        def process_chunk(chunk):
            detailed_prompt = self.create_detailed_prompt(input_data, chunk)
            raw_details = self.get_openai_response(detailed_prompt, str(input_data.dict()))
            details_json = json.loads(self.clean_json(raw_details))
            return details_json.get("days", [])

        # Step 3: Run all chunk requests in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(process_chunk, chunks)

        for chunk_days in results:
            detailed_days.extend(chunk_days)

        # Sort by day_number
        detailed_days.sort(key=lambda x: x["day_number"])

        # Step 4: Build final response
        response_json = {
            "itinerary_id": str(uuid4()),  # Generate a unique itinerary ID
            "status": "COMPLETED",          # Set status to "COMPLETED"
            "current_activity": detailed_days[0]["activities"][0] if detailed_days and detailed_days[0]["activities"] else None,
            "day_plan": detailed_days[0]["activities"] if detailed_days else [],
            "user_info": {
                "total_adults": input_data.total_adults,
                "total_children": input_data.total_children,
                "destination": input_data.destination,
                "location": input_data.location,
                "departure_date": input_data.departure_date,
                "return_date": input_data.return_date,
                "amenities": input_data.amenities,
                "activities": input_data.activities,
                "pacing": input_data.pacing,
                "food": input_data.food,
                "special_note": input_data.special_note
            },
            "days": detailed_days
        }

        return ai_suggestion_response(
            success=True,
            message="Itinerary generated successfully.",
            data=response_json
        )

    
    def create_outline_prompt(self, input_data: ai_suggestion_request, trip_days: int) -> str:
        return f"""You are a travel planner AI.

Generate a structured JSON itinerary outline for a {trip_days}-day trip to {input_data.destination} starting on {input_data.departure_date}. 
ONLY include this structure per day:

- day_number (integer)
- date (YYYY-MM-DD)
- places (list of 2–4 unique attractions/activities per day, brief names only)

DO NOT include full descriptions or times. Only suggest unique, culturally and logistically appropriate activities. No duplication.

Return only valid JSON in this format:

{{
  "days": [
    {{
      "day_number": 1,
      "date": "YYYY-MM-DD",
      "places": ["Place 1", "Place 2", "Place 3"]
    }},
    ...
  ]
}}"""

    def create_detailed_prompt(self, input_data: ai_suggestion_request, day_chunk: list) -> str:
        day_info = "\n".join(
            f"Day {day['day_number']} ({day['date']}): {', '.join(day['places'])}"
            for day in day_chunk
        )

        return f"""You are an expert travel planner AI. Based on the given per-day list of places, generate a detailed JSON travel itinerary.

    **TRAVEL DETAILS**
    - Travelers: {input_data.total_adults} adults, {input_data.total_children} children
    - Destination: {input_data.destination}
    - Accessibility/Amenities: {', '.join(input_data.amenities)}
    - Interests: {', '.join(input_data.activities)}
    - Food Preferences: {', '.join(input_data.food)}
    - Pacing: {', '.join(input_data.pacing)}
    - Special Notes: {input_data.special_note or 'None'}

    ---

    **ASSIGNED DAYS**
    {day_info}

    ---

    **INSTRUCTIONS**
    - Only generate days assigned above
    - Each day should have 2–4 activities
    - Activities should flow logically (morning → evening)
    - Consider accessibility, age group, and pacing
    - Use appropriate keywords: ["Travel", "Meal", "Relaxation", "Cultural", "Outdoor", "Leisure", "Historical", "Museum", "Shopping", "Backup"]

    ---

    **EXAMPLE OUTPUT FORMAT** (JSON only, no markdown):

    {{
    "days": [
        {{
        "day_number": 1,
        "date": "2025-09-20",
        "activities": [
            {{
            "id": "activity-uuid-1",
            "time": "8:00 AM",
            "title": "Breakfast at Hotel",
            "description": "Start the day with a healthy breakfast at the hotel's wheelchair-accessible restaurant.",
            "place": "Hotel Restaurant",
            "keyword": "Meal"
            }},
            {{
            "id": "activity-uuid-2",
            "time": "10:00 AM",
            "title": "Visit Senso-ji Temple",
            "description": "Explore Tokyo's oldest temple with wide pathways suitable for wheelchairs. Learn about local religious traditions.",
            "place": "Senso-ji Temple",
            "keyword": "Cultural"
            }},
            {{
            "id": "activity-uuid-3",
            "time": "1:00 PM",
            "title": "Lunch at Asakusa District",
            "description": "Enjoy a traditional Japanese lunch with vegetarian options available, in an accessible setting.",
            "place": "Asakusa Dining Area",
            "keyword": "Meal"
            }}
        ]
        }}
    ]
    }}

    ---

    ONLY return valid JSON following this structure. Do not return explanations or markdown. All activities must reflect the assigned places."""


    def get_openai_response(self, prompt: str, data: str) -> str:
        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": data}
            ]
        )
        return completion.choices[0].message.content.strip()

    def calculate_trip_days(self) -> int:
        departure = datetime.datetime.strptime(self.departure_date, '%Y-%m-%d')
        return_date = datetime.datetime.strptime(self.return_date, '%Y-%m-%d')
        return (return_date - departure).days + 1

    def clean_json(self, raw: str) -> str:
        if raw.startswith("```json"):
            return raw[7:].strip("` \n")
        if raw.startswith("```"):
            return raw[3:].strip("` \n")
        return raw
