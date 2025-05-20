# from fastapi import APIRouter, HTTPException
# from fastapi.responses import FileResponse
# from pydantic import BaseModel
# from app.services.image_generator import generate_image
#
# router = APIRouter()
#
#
# class ImageRequest(BaseModel):
#     prompt: str
#
#
# @router.post("/generate-image/")
# async def generate_image_endpoint(request: ImageRequest):
#     """Generates an image based on user input and returns the file."""
#     if not request.prompt.strip():
#         raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
#
#     image_path = generate_image(request.prompt)
#
#     if not image_path:
#         raise HTTPException(status_code=500, detail="Failed to generate image.")
#
#     return FileResponse(image_path, media_type="image/jpeg", filename="generated_image.jpg")

from fastapi import APIRouter, HTTPException, Response
from app.services.image_generator import generate_image, MODELS
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ImageRequest(BaseModel):
    prompt: str
    model: Optional[str] = None


@router.post("/generate-image/")
async def generate_image_endpoint(request: ImageRequest):
    try:
        if not request.prompt.strip():
            raise HTTPException(
                status_code=400,
                detail={"error": "Prompt cannot be empty"}
            )

        image_data = generate_image(request.prompt)

        if not image_data:
            raise HTTPException(
                status_code=500,
                detail={"error": "Received empty image data from model"}
            )

        return Response(
            content=image_data,
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=generated_image.png"}
        )

    except HTTPException:
        raise  # Re-raise HTTPException as is
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "message": "Image generation failed",
                "supported_models": MODELS
            }
        )