# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# import logging
# from app.services.social_media_poster import post_to_instagram
#
# router = APIRouter()
#
# class PostRequest(BaseModel):
#     image_url: str
#     caption: str
#     access_token: str
#
# @router.post("/post-now/")
# async def post_now(request: PostRequest):
#     logging.info(f"📩 Received request: {request.dict()}")  # Log incoming request
#
#     if not request.access_token:
#         raise HTTPException(status_code=400, detail="Missing access_token. Please reconnect Instagram.")
#
#     result = post_to_instagram(request.image_url, request.caption, request.access_token)
#
#     # Log API response for debugging
#     logging.info(f"📡 Instagram API Response: {result}")
#
#     if "error" in result:
#         raise HTTPException(status_code=400, detail=result["error"])
#
#     return result

import logging
from fastapi import APIRouter, HTTPException, Body
import requests
from datetime import datetime
from app.database import connected_accounts_collection
import httpx

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/post-now/")
async def post_now(data: dict = Body(...)):
    """
    Post content to a social media platform immediately

    Supported platforms: linkedin

    Request body should include:
    - platform: social media platform name
    - caption: content to post
    - image_url: optional image URL (string or array of strings for carousel)
    """
    try:
        platform = data.get("platform", "").lower()
        caption = data.get("caption")
        image_url = data.get("image_url")
        user_id = data.get("user_id", "current_user_id")

        if not platform:
            raise HTTPException(status_code=400, detail="Platform is required")

        if not caption:
            raise HTTPException(status_code=400, detail="Caption/content is required")

        # Validate platform is supported
        valid_platforms = ["linkedin", "facebook", "instagram", "twitter"]
        if platform not in valid_platforms:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported platform. Must be one of: {', '.join(valid_platforms)}"
            )

        # Get connected account for this platform
        account = await connected_accounts_collection.find_one({
            "user_id": user_id,
            "platform": platform,
            "is_active": True
        })

        if not account:
            raise HTTPException(
                status_code=404,
                detail=f"No connected {platform} account found. Please connect your account first."
            )

        # Handle posting based on platform
        if platform == "linkedin":
            response = await post_to_linkedin(account, caption, image_url)

        elif platform == "facebook":
            # Placeholder for Facebook posting
            raise HTTPException(status_code=501, detail="Facebook posting not implemented yet")

        elif platform == "instagram":
            # Placeholder for Instagram posting
            raise HTTPException(status_code=501, detail="Instagram posting not implemented yet")

        elif platform == "twitter":
            # Placeholder for Twitter posting
            raise HTTPException(status_code=501, detail="Twitter posting not implemented yet")

        return {
            "success": True,
            "id": response.get("post_id"),
            "platform": platform,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        logger.error(f"Error in post_now: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to post content: {str(e)}")


async def post_to_linkedin(account, content, image_url=None):
    """
    Post content to LinkedIn using the connected account
    """
    # Determine the correct LinkedIn account URL
    user_urn = f"urn:li:person:{account['account_id']}" if account[
                                                               "account_type"] == "personal" else f"urn:li:organization:{account['account_id']}"

    # Post using LinkedIn API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/api/linkedin/post",  # Call the LinkedIn post endpoint
            json={
                "account_id": account["account_id"],
                "content": content,
                "image_url": image_url,
                "user_id": account["user_id"]
            }
        )

        if response.status_code != 200:
            error_detail = response.json().get("detail", "Unknown error")
            raise HTTPException(status_code=response.status_code, detail=f"LinkedIn posting failed: {error_detail}")

        return response.json()