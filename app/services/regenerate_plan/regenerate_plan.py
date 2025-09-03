import os
import json
import openai
from dotenv import load_dotenv
from .regenerate_plan_schema import regenerate_plan_response,regenerate_plan_request

load_dotenv()

class RegeneratePlan:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def regenerate_plan (self, input_data=regenerate_plan_request) -> regenerate_plan_response:
        prompt = self.create_prompt()
        response = self.get_openai_response(prompt, input_data)
        return response
    
    def create_prompt(self) -> str:
        return f"""You are an expert travel planner specializing in modifying and improving travel itineraries based on user feedback. A traveler wants to change a specific part of their itinerary.

                CURRENT ITINERARY:
                {self.current_plan}

                USER REQUESTED CHANGE:
                {self.user_change}

                DESTINATION CITY:
                {self.place}

                INSTRUCTIONS:
                1. Search the web for current information about {self.place} related to the user's requested change
                2. Analyze the current itinerary to understand the context (time slot, duration, group size, etc.)
                3. Provide multiple relevant alternatives based on the user's request
                4. Consider factors like:
                - Time constraints from the original plan
                - Travel distance from other activities
                - Operating hours and current availability
                - Weather conditions if applicable
                - Group suitability (family-friendly if children mentioned)
                - Current pricing and booking requirements

                OUTPUT FORMAT:

                **SUGGESTED ALTERNATIVES:**

                **Option 1: [Name of Place/Activity]**
                - Time: [Same time slot as original or adjusted if needed]
                - Location: [Full address and area]
                - Description: [Brief description of the activity/place]
                - Why it fits: [How it matches the user's request]
                - Duration: [Estimated time needed]
                - Cost: [Current pricing if available]
                - Booking: [Reservation requirements or walk-in availability]

                **Option 2: [Name of Place/Activity]**
                - Time: [Same time slot as original or adjusted if needed]
                - Location: [Full address and area]
                - Description: [Brief description of the activity/place]
                - Why it fits: [How it matches the user's request]
                - Duration: [Estimated time needed]
                - Cost: [Current pricing if available]
                - Booking: [Reservation requirements or walk-in availability]

                **Option 3: [Name of Place/Activity]**
                - Time: [Same time slot as original or adjusted if needed]
                - Location: [Full address and area]
                - Description: [Brief description of the activity/place]
                - Why it fits: [How it matches the user's request]
                - Duration: [Estimated time needed]
                - Cost: [Current pricing if available]
                - Booking: [Reservation requirements or walk-in availability]

                **RECOMMENDED CHOICE:**
                [Indicate which option is the best fit and why]

                **TIME ADJUSTMENTS:**
                [If the change affects timing of other activities, suggest any necessary adjustments to the rest of the day]

                **ADDITIONAL NOTES:**
                - Transportation between locations
                - Any special considerations (weather, seasonal availability, etc.)
                - Backup options if primary choice is unavailable

                IMPORTANT: 
                - Use web search to find current, accurate information about all suggested alternatives
                - Ensure all suggestions are actually available in {self.place}
                - Provide realistic timing and practical advice
                - Consider the flow of the entire day when making suggestions"""
    
    def get_openai_response(self, prompt: str, data: str) -> regenerate_plan_response:
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": data}],
            temperature=0.7            
        )
        raw_content = completion.choices[0].message.content.strip()
        
    
        return 