from fastapi import APIRouter, HTTPException, Body
from .regenerate_plan import Story
from .regenerate_plan_schema import regenerate_plan_response,regenerate_plan_request

router = APIRouter()
story = Story()

@router.post("/regenerate_plan", response_model= regenerate_plan_response)
async def get_regenerated_plan(request_data=regenerate_plan_request):
    try:
        response = story.regenerate_plan(request_data)
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
