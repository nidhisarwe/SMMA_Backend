from fastapi import APIRouter, HTTPException, Response, Depends
from app.services.image_generator import generate_image, MODELS
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ImageGenerationRequest(BaseModel):
    prompt: str
    model: Optional[str] = None


@router.options("/generate-image/")
async def generate_image_options():
    # Handle preflight requests
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

@router.post("/generate-image/")
async def generate_image_endpoint(request: ImageGenerationRequest):
    try:
        
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(
                status_code=400,
                detail={"error": "Prompt cannot be empty"}
            )

        # Log the incoming request
        logger.info(f"Image generation request received with prompt: {request.prompt[:50]}..." if len(request.prompt) > 50 else f"Image generation request received with prompt: {request.prompt}")
        
        # Generate the image
        image_data = generate_image(request.prompt)

        if not image_data:
            logger.error("Empty image data returned from generator")
            raise HTTPException(
                status_code=500,
                detail={"error": "Received empty image data from model"}
            )

        logger.info("Image successfully generated, returning response")
        response = Response(
            content=image_data,
            media_type="image/png"
        )
        
        # Add CORS headers to the response
        response.headers["Content-Disposition"] = "inline; filename=generated-image.png"
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        
        return response

    except HTTPException:
        raise  # Re-raise HTTPException as is
    except ValueError as e:
        # Handle validation errors
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid input",
                "message": str(e)
            }
        )
    except Exception as e:
        # Log the full error
        logger.error(f"Image generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to generate image",
                "message": str(e),
                "supported_models": MODELS
            }
        )