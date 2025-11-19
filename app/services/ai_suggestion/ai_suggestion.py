import os
import json
import asyncio
import datetime
import logging
from uuid import uuid4
from typing import Any, Callable, List, Tuple

from dotenv import load_dotenv
from openai import AsyncOpenAI
from fastapi import HTTPException

from .ai_suggestion_schema import ai_suggestion_response, ai_suggestion_request

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AISuggestion:
    """AISuggestion -- single-file, drop-in replacement.

    Features:
    - short-trip (<=5 days) single-shot prompt
    - long-trip (>5 days) outline -> chunk -> parallel detailed prompts
    - robust JSON cleaning & parsing
    - concurrency semaphore + retry/backoff
    - UUID generation for itinerary_id (you can replace with DB ids)

    Note: this expects an AsyncOpenAI client (openai package) and a pydantic-like
    ai_suggestion_request with `.json()` available. If you don't use FastAPI,
    replace HTTPException with appropriate exceptions.
    """

    def __init__(self, concurrency_limit: int = 5, max_retries: int = 2):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.concurrency_limit = concurrency_limit
        self.max_retries = max_retries
        
    async def get_suggestion(self, input_data: ai_suggestion_request) -> ai_suggestion_response:
        try:
            dep = datetime.datetime.strptime(input_data.departure_date, "%Y-%m-%d")
            ret = datetime.datetime.strptime(input_data.return_date, "%Y-%m-%d")
        except Exception:
            raise HTTPException(status_code=400, detail="Dates must be in YYYY-MM-DD format.")

        if ret < dep:
            raise HTTPException(status_code=400, detail="return_date must be the same or after departure_date.")

        trip_days = (ret - dep).days + 1

        logger.info("Generating itinerary for %s -> %s (%d days)", input_data.departure_date, input_data.return_date, trip_days)

        if trip_days <= 4:
            logger.info("Using SHORT TRIP path")
            return await self.handle_short_trip(input_data, trip_days)
        else:
            logger.info("Using LONG TRIP path")
            return await self._handle_long_trip(input_data, trip_days)

    # short-trip path (<=4 days)
    async def handle_short_trip(self, input_data: ai_suggestion_request, trip_days: int) -> ai_suggestion_response:
        logger.info("SHORT TRIP: Starting processing for %d days", trip_days)
        itinerary_id = f"itinerary-{uuid4()}"
        prompt = self.create_short_trip_prompt(input_data, trip_days, itinerary_id)

        raw = await self._call_with_retries(lambda: self.get_openai_response(prompt, input_data))
        cleaned = self.clean_json(raw)

        try:
            parsed = json.loads(cleaned)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"LLM returned invalid JSON: {e}")

        # Extract data from the response structure
        if "data" in parsed:
            response_data = parsed["data"]
        else:
            response_data = parsed

        return ai_suggestion_response(
            success=True,
            message="Itinerary (short trip) generated successfully.",
            data=response_data,
        )

    def create_short_trip_prompt(self, input_data: ai_suggestion_request, trip_days: int, itinerary_id: str) -> str:
        return f"""You are an expert travel planner AI. Use web search to find current, accurate information about {input_data.destination}.

    TRAVEL DETAILS:
    - Trip Duration: {trip_days} days
    - Travelers: {input_data.total_adults} adults, {input_data.total_children} children (under 12)
    - Destination: {input_data.destination}, {input_data.destination_state}
    - Departure Date: {input_data.departure_date}
    - Return Date: {input_data.return_date}

    PREFERENCES:
    - Activities: {', '.join(input_data.activities)}
    - Amenities: {', '.join(input_data.amenities)}
    - Food: {', '.join(input_data.food)}
    - Pacing: {', '.join(input_data.pacing)}
    - Special Notes: {input_data.special_note or 'None specified'}

    Search the web for real places, restaurants, hotels, and current events that match these preferences. 
    
    Generate a SHORT title for this itinerary using only 2-3 words that reflects the trip's main theme (e.g., "Cultural Moscow", "Tokyo Adventures", "Paris Discovery"). You MUST choose exactly one category from this list based on the planned activities: "Cultural & Heritage", "Museums & Art", "Food & Culinary Experiences", "Outdoor & Nature", "Shopping & Fashion", "Leisure & Relaxation", "Family-Friendly Activities", "Accessibility-Friendly", "Local Experiences", "Historical Sites", "Photography & Scenic Spots", "Wellness & Spa", "Adventure & Outdoor Sports", "Seasonal & Festive", "Shopping & Souvenirs".
    
    Keywords to use for activities: [
  "outdoor",
  "hotel"
  "meal",
  "leisure",
  "museum",
  "cultural",
  "adventure",
  "nature",
  "shopping",
  "entertainment",
  "romantic",
  "water",
  "wildlife",
  "sports",
  "spa",
  "amenity_workspace",
  "amenity_game_room",
  "amenity_gym",
  "amenity_pool",
  "amenity_parking",
  "amenity_outdoor_space",
  "pace_relaxed",
  "pace_balanced",
  "pace_fast",
  "food_casual",
  "food_fine",
  "food_local",
  "food_asian",
  "food_italian",
  "food_mexican",
  "service_transport"
    ]
    IMPORTANT: Return ONLY valid JSON, no markdown, no comments:

    {{
    "success": true,
    "data": {{
        "title": "Short Title",
        "category": "Cultural & Heritage",
        "days": [
        {{
            "day_number": 1,
            "day_uuid": "day-1-{itinerary_id}",
            "date": "{input_data.departure_date}",
            "activities": [
            {{
                "time": "9:00 AM",
                "title": "Airport Arrival",
                "description": "Arrive at {input_data.destination} Airport and proceed through customs and baggage claim",
                "place": "{input_data.destination} Airport",
                "keyword": "arrival"
            }},
            {{
                "time": "10:30 AM",
                "title": "Hotel Check-in",
                "description": "Check-in at [Real Hotel Name that matches amenities]",
                "place": "[Real Hotel Name]",
                "keyword": "hotel"
            }},
            {{
                "time": "12:00 PM", 
                "title": "[Real Restaurant/Dining Experience]",
                "description": "Description matching food preferences",
                "place": "[Real Restaurant Name]",
                "keyword": "meal"
            }},
            {{
                "time": "2:00 PM",
                "title": "[Real Attraction/Activity]",
                "description": "Activity description matching user interests and any current special events",
                "place": "[Real Venue Name]", 
                "keyword": "amenity_outdoor_space"
            }}
            ]
        }}
        ],
        "status": "COMPLETED"
    }},
    "message": "Itinerary generated successfully"
    }}

    Generate {trip_days} days of activities. Use real place names found through web search that match the user's preferences."""

    # long-trip path (>4 days)
    async def _handle_long_trip(self, input_data: ai_suggestion_request, trip_days: int) -> ai_suggestion_response:
        logger.info("LONG TRIP: Starting processing for %d days", trip_days)
        
        # 1) Outline pass
        itinerary_id = f"itinerary-{uuid4()}"
        outline_prompt = self.create_outline_prompt(input_data, trip_days)
        raw_outline = await self._call_with_retries(lambda: self.get_openai_response(outline_prompt, input_data))
        outline_clean = self.clean_json(raw_outline)

        try:
            outline_obj = json.loads(outline_clean)
        except Exception as e:
            logger.error("Failed parsing outline JSON: %s\nCleaned (truncated): %s\nRaw (truncated): %s", e, outline_clean[:2000], raw_outline[:2000])
            raise HTTPException(status_code=502, detail=f"LLM returned invalid outline JSON: {e}")

        days_outline = outline_obj.get("days", [])
        title = outline_obj.get("title", f"Trip to {input_data.destination}")
        category = outline_obj.get("category", "Cultural & Heritage")
        logger.info("Outline generated %d days", len(days_outline))
        
        if not days_outline:
            raise HTTPException(status_code=502, detail="Outline returned empty days")

        # 2) chunk the days
        chunk_size = 4
        chunks = [days_outline[i : i + chunk_size] for i in range(0, len(days_outline), chunk_size)]
        logger.info("Split into %d chunks of max size %d", len(chunks), chunk_size)

        # 3) process chunks in parallel but with concurrency limit and proper merging
        sem = asyncio.Semaphore(self.concurrency_limit)

        async def worker(chunk: List[dict], idx: int,itinerary_id:str) -> Tuple[int, List[dict]]:
            async with sem:
                logger.info("Worker %d processing chunk with %d days", idx, len(chunk))
                prompt = self.create_detailed_prompt(input_data, chunk,itinerary_id)
                raw = await self._call_with_retries(lambda: self.get_openai_response(prompt, input_data))
                cleaned = self.clean_json(raw)
                try:
                    parsed = json.loads(cleaned)
                except Exception as e:
                    logger.error("Failed parsing detailed chunk %s: %s\nCleaned (truncated): %s\nRaw (truncated): %s", idx, e, cleaned[:2000], raw[:2000])
                    raise HTTPException(status_code=502, detail=f"LLM returned invalid JSON for chunk {idx}: {e}")

                # Handle different response structures
                days = []
                if "days" in parsed:
                    days = parsed["days"]
                elif "data" in parsed and "days" in parsed["data"]:
                    days = parsed["data"]["days"]
                elif isinstance(parsed, list):
                    days = parsed 
                
                logger.info("Worker %d successfully processed %d days", idx, len(days))
                return idx, days

        tasks = [worker(chunk, i, itinerary_id) for i, chunk in enumerate(chunks)]

        results = await asyncio.gather(*tasks)

        # 4) merge preserving order
        results_sorted = sorted(results, key=lambda x: x[0])
        merged_days: List[dict] = []
        for idx, days in results_sorted:
            merged_days.extend(days)
        
        logger.info("Merged %d total days from all workers", len(merged_days))

        response_obj = {
            "success": True,
            "data": {
                "title": title,
                "category": category,
                "days": merged_days, 
                "status": "COMPLETED"
            },
            "message": "Itinerary generated successfully",
        }

        return ai_suggestion_response(success=True, message="Itinerary generated successfully.", data=response_obj["data"])

    def create_outline_prompt(self, input_data: ai_suggestion_request, trip_days: int) -> str:
        return f"""You are a travel planner AI.

Generate a structured JSON itinerary outline for a {trip_days}-day trip to {input_data.destination} starting on {input_data.departure_date}.
ONLY include this structure per day:

- day_number (integer)
- date (YYYY-MM-DD)
- places (list of 2–4 unique attractions/activities per day, brief names only)

DO NOT include full descriptions or times. Only suggest unique, culturally and logistically appropriate activities. No duplication. 

Generate a SHORT title for this itinerary using only 2-3 words that reflects the trip's main theme (e.g., "Cultural Moscow", "Tokyo Adventures", "Paris Discovery"). You MUST choose exactly one category from this list based on the planned activities: "Cultural & Heritage", "Museums & Art", "Food & Culinary Experiences", "Outdoor & Nature", "Shopping & Fashion", "Leisure & Relaxation", "Family-Friendly Activities", "Accessibility-Friendly", "Local Experiences", "Historical Sites", "Photography & Scenic Spots", "Wellness & Spa", "Adventure & Outdoor Sports", "Seasonal & Festive", "Shopping & Souvenirs".

Return only valid JSON in this format:

{{
  "title": "Short Title",
  "category": "Cultural & Heritage",
  "days": [
    {{
      "day_number": 1,
      "date": "YYYY-MM-DD",
      "places": ["Place 1", "Place 2", "Place 3"]
    }},
    ...
  ]
}}"""

    def create_detailed_prompt(self, input_data: ai_suggestion_request, day_chunk: List[dict], itinerary_id: str) -> str:
        day_info = "\n".join(
            f"Day {day['day_number']} ({day['date']}): {', '.join(day['places'])}"
            for day in day_chunk
        )

        return f"""You are an expert travel planner AI. Based on the given per-day list of places, generate a detailed JSON travel itinerary.

    TRAVEL DETAILS
    - Travelers: {input_data.total_adults} adults, {input_data.total_children} children
    - Destination: {input_data.destination}
    - Accessibility/Amenities: {', '.join(input_data.amenities)}
    - Interests: {', '.join(input_data.activities)}
    - Food Preferences: {', '.join(input_data.food)}
    - Pacing: {', '.join(input_data.pacing)}
    - Special Notes: {input_data.special_note or 'None'}

    ---

    ASSIGNED DAYS
    {day_info}

    ---

    INSTRUCTIONS
    - Only generate days assigned above
    - Each day should have 2–4 activities
    - Activities should flow logically (morning → evening)
    - Consider accessibility, age group, and pacing
    - Use appropriate keywords: ["Travel", "Meal", "Relaxation", "Cultural", "Outdoor", "Leisure", "Historical", "Museum", "Shopping", "Backup"]

    Return ONLY valid JSON in this exact format:
    {{
    "days": [
        {{
        "day_number": 1,
        "day_uuid": "day-1-{itinerary_id}",
        "date": "YYYY-MM-DD",
        "activities": [
            {{
            "time": "9:00 AM",
            "title": "Activity title",
            "description": "Brief activity description",
            "place": "Place name",
            "keyword": "activity-type"
            }}
        ]
        }}
    ]
    }}

    IMPORTANT: Return only the JSON object with the "days" array. Do not include any other text or markdown."""

    async def get_openai_response(self, prompt: str, data_obj: Any) -> str:
        if hasattr(data_obj, "json") and callable(getattr(data_obj, "json")):
            data_json = data_obj.json()
        else:
            data_json = json.dumps(data_obj)

        completion = await self.client.chat.completions.create(
            model="gpt-4o-search-preview",
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": data_json}],
        )

        return completion.choices[0].message.content.strip()

    async def _call_with_retries(self, func: Callable[[], Any]) -> Any:
        attempt = 0
        while True:
            try:
                return await func()
            except Exception as e:
                attempt += 1
                logger.warning("Attempt %d failed with error: %s", attempt, e)
                if attempt > self.max_retries:
                    logger.error("Max retries reached. Raising error.")
                    raise
                await asyncio.sleep(1.2 ** attempt)

    def calculate_trip_days(self) -> int:
        departure = datetime.datetime.strptime(self.departure_date, "%Y-%m-%d")
        return_date = datetime.datetime.strptime(self.return_date, "%Y-%m-%d")
        return (return_date - departure).days + 1

    def clean_json(self, raw: str) -> str:
        # If already valid JSON, return it
        try:
            json.loads(raw)
            return raw
        except Exception:
            pass

        # Remove backtick fences
        if raw.startswith("```json"):
            raw = raw[len("```json"):].strip()
        elif raw.startswith("```"):
            raw = raw[len("```"):].strip()

        # Extract first { ... } pair as candidate
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = raw[start : end + 1]
            try:
                json.loads(candidate)
                return candidate
            except Exception:
                pass
        return raw
