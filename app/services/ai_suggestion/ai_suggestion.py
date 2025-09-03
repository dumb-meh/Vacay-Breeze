import os
import json
import openai
from dotenv import load_dotenv
from .ai_suggestion_schema import ai_suggestion_response
import datetime

load_dotenv ()

class AISuggestion:
    def __init__(self):
        self.client=openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def get_suggestion(self, input_data:str)->ai_suggestion_response:
        prompt=self.create_prompt()
        data=input_data
        response=self.get_openai_response (prompt,data)
        return response
    
    def create_prompt(self) -> str:
        return f"""You are an expert travel planner specializing in creating detailed, personalized itineraries. Based on the provided travel preferences, create a comprehensive day-by-day travel plan.

                TRAVEL DETAILS:
                - Travelers: {self.total_adults} adults, {self.total_children} children (under 12)
                - Destination: {self.destination}
                - Current Location: {self.location}
                - Departure Date: {self.departure_date}
                - Return Date: {self.return_date}
                - Trip Duration: {self.calculate_trip_days()} days

                ACCOMMODATION PREFERENCES:
                Amenities : {self.amenities}
                

                ACTIVITY PREFERENCES:
                Preferred Activities: {self.activities}

                VACATION PACE:
                {self.pacing}

                DINING PREFERENCES:
                Food Experience: {self.food}

                SPECIAL REQUIREMENTS:
                {self.special_notes}

                INSTRUCTIONS:
                1. Create a detailed day-by-day itinerary with specific times, locations, and activities
                2. Consider the vacation pace preference when scheduling activities
                3. Include family-friendly options when children are present
                4. Incorporate preferred activities and dining experiences
                5. Suggest accommodations that meet the specified amenities
                6. Account for travel time between locations
                7. Include backup indoor activities for potential weather issues
                8. Provide estimated costs where applicable
                9. Consider the group size when making recommendations

                OUTPUT FORMAT:
                **TOUR SUMMARY:**
                [Provide a brief 2-3 sentence overview of the trip highlighting key experiences]

                **ACCOMMODATION RECOMMENDATION:**
                [Suggest specific hotels/accommodations that match the amenities requirements]

                **DETAILED ITINERARY:**

                **Day 1 ({self.departure_date}):**
                9:00 AM    - Arrive at {self.destination_city} Airport
                10:30 AM   - Check-in at [Hotel Name]
                12:00 PM   - Lunch at [Restaurant Name] - [Cuisine Type]
                2:00 PM    - [Activity/Attraction]
                5:00 PM    - [Activity/Attraction]
                7:30 PM    - Dinner at [Restaurant Name]
                9:00 PM    - [Evening activity or rest]

                [Continue this format for each day]

                **Day {self.calculate_trip_days()} ({self.return_date}):**
                [Final day activities leading to departure]

                **ADDITIONAL RECOMMENDATIONS:**
                - Current local transportation options and pricing
                - Emergency contacts and important phone numbers
                - Weather forecast and packing suggestions for travel dates
                - Cultural etiquette tips if traveling internationally
                - Current budget estimates for activities and meals
                - Real-time booking links where available
                - Local COVID-19 or health guidelines if applicable

                **BACKUP PLANS:**
                [Alternative indoor activities in case of weather issues, with current availability]

                **CURRENT EVENTS & SEASONAL HIGHLIGHTS:**
                [Any festivals, events, or seasonal attractions happening during the travel dates]

                IMPORTANT: Use web search to ensure all information is current and accurate for the specified travel dates. Include real establishments, current pricing, and up-to-date availability information."""
            
    def get_openai_response (self, prompt:str, data:str)->str:
        completion =self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"system", "content": prompt},{"role":"user", "content": data}],
            temperature=0.7            
        )
        return completion.choices[0].message.content
    def calculate_trip_days(self) -> int:
        departure = datetime.strptime(self.departure_date, '%Y-%m-%d')
        return_date = datetime.strptime(self.return_date, '%Y-%m-%d')
        return (return_date - departure).days + 1
    
