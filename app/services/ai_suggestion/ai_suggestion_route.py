from fastapi import APIRouter,HTTPException
from .ai_suggestion import AISuggestion
from .ai_suggestion_schema import ai_suggestion_response,ai_suggestion_request

router= APIRouter()
suggestion=AISuggestion()

@router.post("/ai_suggestion",response_model=ai_suggestion_response)
async def get_ai_suggestion(request_data=ai_suggestion_request):
    try:
        response=suggestion.get_suggestion(request_data)
        return ai_suggestion_request (response=response)
    
    except Exception as e:
        raise HTTPException (status_code=500, detail=str(e))