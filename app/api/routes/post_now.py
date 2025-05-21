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
        is_carousel = data.get("is_carousel", False)

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

        # Process the image_url based on is_carousel flag
        processed_image_url = None
        if image_url:
            if isinstance(image_url, list):
                if is_carousel:
                    # For carousel posts, keep the list
                    processed_image_url = image_url
                else:
                    # For non-carousel posts, use the first image
                    processed_image_url = image_url[0] if image_url else None
            else:
                # Single image URL
                processed_image_url = image_url

        # Handle posting based on platform
        if platform == "linkedin":
            response = await post_to_linkedin(account, caption, processed_image_url)

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
    try:
        # Determine the correct LinkedIn account URN based on account_type
        user_urn = None

        if account.get("account_type") == "personal":
            user_urn = f"urn:li:person:{account['account_id_on_platform']}"
        else:  # Company/organization account
            user_urn = f"urn:li:organization:{account['account_id_on_platform']}"

        logger.info(f"Posting to LinkedIn as: {user_urn}")
        logger.info(f"Content: {content}")
        logger.info(f"Image URL: {image_url}")

        # Prepare the request payload
        request_payload = {
            "account_id": account["account_id_on_platform"],
            "content": content,
            "user_id": account["user_id"]
        }

        # Handle image_url based on whether it's a carousel or single image
        if image_url:
            # For LinkedIn, we pass the image URL as is (the LinkedIn service will handle
            # the array case by taking the first image for carousel posts)
            request_payload["image_url"] = image_url

        # Make the API call to the LinkedIn endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://127.0.0.1:8000/api/linkedin/post",  # Call the LinkedIn post endpoint
                json=request_payload,
                timeout=60  # Increase timeout for image processing
            )

            if response.status_code != 200:
                error_detail = response.json().get("detail", "Unknown error")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"LinkedIn posting failed: {error_detail}"
                )

            result = response.json()
            logger.info(f"LinkedIn post response: {result}")
            return result

    except httpx.TimeoutException:
        logger.error("LinkedIn posting request timed out")
        raise HTTPException(
            status_code=504,
            detail="LinkedIn posting timed out. This might be due to slow image processing."
        )
    except Exception as e:
        logger.error(f"Error posting to LinkedIn: {str(e)}")
        raise