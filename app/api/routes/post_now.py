import logging
from fastapi import APIRouter, HTTPException, Body, Depends
from datetime import datetime
from app.database import connected_accounts_collection
from app.api.dependencies import auth_required
import httpx

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/post-now/")
async def post_now(data: dict = Body(...), current_user_id: str = Depends(auth_required)):
    """
    Post content to a social media platform immediately

    Supported platforms: linkedin

    Request body should include:
    - platform: social media platform name
    - caption: content to post
    - image_url: optional image URL (string or array of strings for carousel)
    - is_carousel: boolean indicating if the post is a carousel
    """
    try:
        platform = data.get("platform", "").lower()
        caption = data.get("caption")
        image_url = data.get("image_url")
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
            "user_id": current_user_id,  # Use authenticated user ID
            "platform": platform,
            "is_active": True
        })

        if not account:
            raise HTTPException(
                status_code=404,
                detail=f"No connected {platform} account found. Please connect your account first."
            )

        # Check for token expiration
        if account.get("expires_at") and account["expires_at"] < datetime.utcnow():
            logger.warning(f"Access token expired for LinkedIn account {account['account_id_on_platform']}")
            raise HTTPException(
                status_code=401,
                detail="LinkedIn access token has expired. Please reconnect your account."
            )

        # Process the image_url based on is_carousel flag
        processed_image_url = None
        if image_url:
            logger.info(f"Raw image_url received: {image_url}")
            if isinstance(image_url, list):
                if is_carousel:
                    processed_image_url = image_url
                    logger.info(f"Using carousel images: {processed_image_url}")
                else:
                    processed_image_url = image_url[0] if image_url and len(image_url) > 0 else None
                    logger.info(f"Using first image from list: {processed_image_url}")
            else:
                processed_image_url = image_url
                logger.info(f"Using single image: {processed_image_url}")
        else:
            logger.warning("No image_url provided in request")
            
        # Ensure image_url is not empty or None
        if processed_image_url == "" or (isinstance(processed_image_url, list) and len(processed_image_url) == 0) or processed_image_url == [] or processed_image_url is None:
            logger.warning("Empty image_url detected, setting to None")
            processed_image_url = None

        # Handle posting based on platform
        if platform == "linkedin":
            response = await post_to_linkedin(account, caption, processed_image_url)

        elif platform == "facebook":
            raise HTTPException(status_code=501, detail="Facebook posting not implemented yet")

        elif platform == "instagram":
            raise HTTPException(status_code=501, detail="Instagram posting not implemented yet")

        elif platform == "twitter":
            raise HTTPException(status_code=501, detail="Twitter posting not implemented yet")

        return {
            "success": True,
            "id": response.get("post_id"),
            "platform": platform,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in post_now for user {current_user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to post content: {str(e)}")

async def post_to_linkedin(account, content, image_url=None):
    """
    Post content to LinkedIn using the connected account
    """
    try:
        from app.services.linkedin_service import LinkedInService
        linkedin_service = LinkedInService()

        # Check if token is expired and attempt to refresh
        if account.get("expires_at") and account["expires_at"] < datetime.utcnow():
            logger.info(f"Attempting to refresh token for LinkedIn account {account['account_id_on_platform']}")
            if not account.get("refresh_token"):
                raise HTTPException(
                    status_code=401,
                    detail="No refresh token available. Please reconnect your LinkedIn account."
                )
            
            token_data = await linkedin_service.refresh_token(account["refresh_token"])
            if not token_data:
                raise HTTPException(
                    status_code=401,
                    detail="Failed to refresh LinkedIn access token. Please reconnect your account."
                )

            # Update account with new token data
            await connected_accounts_collection.update_one(
                {"_id": account["_id"]},
                {
                    "$set": {
                        "access_token": token_data["access_token"],
                        "refresh_token": token_data.get("refresh_token", account["refresh_token"]),
                        "expires_at": datetime.utcnow() + timedelta(seconds=token_data["expires_in"]),
                        "updated_at": datetime.utcnow(),
                    }
                }
            )
            account["access_token"] = token_data["access_token"]
            logger.info(f"Successfully refreshed token for LinkedIn account {account['account_id_on_platform']}")

        # Determine the correct LinkedIn account URN based on account_type
        user_urn = None
        if account.get("account_type") == "personal":
            user_urn = f"urn:li:person:{account['account_id_on_platform']}"
        else:  # Company/organization account
            user_urn = f"urn:li:organization:{account['account_id_on_platform']}"

        logger.info(f"Posting to LinkedIn as: {user_urn}")
        logger.info(f"Content: {content}")
        logger.info(f"Image URL: {image_url}")

        # Create the post
        post_id = await linkedin_service.create_post(
            access_token=account["access_token"],
            user_urn=user_urn,
            content=content,
            image_url=image_url
        )

        return {"post_id": post_id}

    except httpx.TimeoutException:
        logger.error("LinkedIn posting request timed out")
        raise HTTPException(
            status_code=504,
            detail="LinkedIn posting timed out. This might be due to slow image processing."
        )
    except Exception as e:
        logger.error(f"Error posting to LinkedIn: {str(e)}")
        raise