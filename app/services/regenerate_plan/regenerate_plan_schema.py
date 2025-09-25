from pydantic import BaseModel
from typing import Dict,List,Any,Union, Optional
class regenerate_plan_request(BaseModel):
    user_search: str
    day_plan:List[Dict[str, Any]]
    user_info: Dict[str, Union[str, int, List[str]]]
    
class regenerate_plan_response(BaseModel):
    success: bool
    data: Dict[str, Any]  
    message: Optional[str]