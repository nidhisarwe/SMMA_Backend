# Backend/app/api/routes/caption_gen.py - FIXED
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
import logging
from app.services.caption_generator import generate_caption

router = APIRouter()
logger = logging.getLogger(__name__)

class CaptionRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000, description="Content description for caption generation")
    platform: str = Field(default="general", description="Target social media platform")
    is_carousel: Optional[bool] = Field(default=False, description="Whether this is for a carousel post")
    max_length: Optional[int] = Field(default=300, ge=50, le=500, description="Maximum caption length")

class CaptionResponse(BaseModel):
    caption: str
    platform: str
    is_carousel: bool
    success: bool
    message: Optional[str] = None

@router.post("/generate-caption/", response_model=CaptionResponse)
async def generate_caption_endpoint(request: CaptionRequest):
    """
    Generate an AI-powered social media caption based on user input.
    
    - **prompt**: Description of what the post is about
    - **platform**: Target platform (instagram, twitter, linkedin, facebook, general)
    - **is_carousel**: Whether this is for a carousel/multi-image post
    - **max_length**: Maximum length for the generated caption
    """
    
    # Validate platform
    valid_platforms = ["instagram", "twitter", "linkedin", "facebook", "general"]
    if request.platform.lower() not in valid_platforms:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}"
        )
    
    # Validate prompt
    if not request.prompt.strip():
        raise HTTPException(
            status_code=400, 
            detail="Prompt cannot be empty or just whitespace."
        )

    try:
        logger.info(f"Generating caption - Platform: {request.platform}, Carousel: {request.is_carousel}, Prompt length: {len(request.prompt)}")
        
        # Generate caption with improved parameters
        caption = generate_caption(
            prompt=request.prompt.strip(),
            max_tokens=request.max_length,
            temperature=0.8,
            platform=request.platform.lower(),
            is_carousel=request.is_carousel
        )
        
        # Validate the generated caption
        if not caption or len(caption.strip()) < 10:
            logger.warning(f"Generated caption too short or empty: '{caption}'")
            raise HTTPException(
                status_code=500,
                detail="Generated caption is too short. Please try with a more detailed prompt."
            )
        
        # Check for error messages in the caption (from service)
        error_indicators = [
            "API key not configured",
            "Failed to connect",
            "Could not generate",
            "timed out",
            "An unexpected error"
        ]
        
        if any(indicator in caption for indicator in error_indicators):
            logger.error(f"Service returned error in caption: {caption}")
            raise HTTPException(
                status_code=500,
                detail=caption  # Return the specific error message
            )
        
        logger.info(f"Successfully generated caption of length {len(caption)}")
        
        return CaptionResponse(
            caption=caption,
            platform=request.platform.lower(),
            is_carousel=request.is_carousel,
            success=True,
            message="Caption generated successfully"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors, etc.)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in caption generation endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during caption generation: {str(e)}"
        )

@router.get("/caption-health/")
async def health_check():
    """Health check endpoint for caption generation service"""
    try:
        # Test with a simple prompt
        test_caption = generate_caption("test post", platform="general")
        
        return {
            "status": "healthy",
            "service": "caption_generation",
            "test_successful": len(test_caption) > 10,
            "available_platforms": ["instagram", "twitter", "linkedin", "facebook", "general"]
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "caption_generation",
            "error": str(e)
        }