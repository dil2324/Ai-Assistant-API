from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    user_id: str = Field(
        min_length = 3,
        max_length = 32,
        pattern = r"^[a-zA-Z0-9_-]+$"
    )
    
    message: str = Field(
        min_length = 1,
        max_length = 3000
        
    )
    
class ChatResponse(BaseModel):
    answer: str