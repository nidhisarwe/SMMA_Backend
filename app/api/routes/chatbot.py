from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ai_engine import generate_response

router = APIRouter()

# Request model
class ChatRequest(BaseModel):
    query: str

@router.post("/chatbot/")
async def chatbot_endpoint(chat: ChatRequest):
    """Receives user input, sends it to AI, and returns AI-generated response."""
    if not chat.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    response = generate_response(chat.query)
    return {"response": response}
