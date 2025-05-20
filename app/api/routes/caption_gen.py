from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.caption_generator import generate_caption

router = APIRouter()

class CaptionRequest(BaseModel):
    prompt: str
    platform: str = "general"

@router.post("/generate-caption/")
async def generate_caption_endpoint(request: CaptionRequest):
    """Generates an AI-powered social media caption based on user input."""
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    try:
        caption = generate_caption(request.prompt, platform=request.platform)
        return {"caption": caption, "platform": request.platform}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
