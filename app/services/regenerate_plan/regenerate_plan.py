import os
import json
import openai
from dotenv import load_dotenv
from .regenerate_plan_schema import regenerate_plan_response

load_dotenv()

class RegeneratePlan:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def regenerate_plan (self, input_data: str) -> regenerate_plan_response:
        prompt = self.create_prompt()
        response = self.get_openai_response(prompt, input_data)
        return response
    
    def create_prompt(self) -> str:
        return f""" """
    
    def get_openai_response(self, prompt: str, data: str) -> regenerate_plan_response:
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": data}],
            temperature=0.7            
        )
        raw_content = completion.choices[0].message.content.strip()
        
    
        return 