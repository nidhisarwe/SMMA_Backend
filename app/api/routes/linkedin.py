import logging
from fastapi import APIRouter, HTTPException, Request, Query, Body
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
from app.services.linkedin_service import LinkedInService
from app.database import connected_accounts_collection, users_collection
from app.models.user import SocialPlatform
from bson import ObjectId, errors as bson_errors
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
linkedin_service = LinkedInService()

FRONTEND_REDIRECT_URI = os.getenv("FRONTEND_REDIRECT_URI",
                                  "http://localhost:5173/social-dashboard")


@router.get("/auth-url")
async def get_linkedin_auth_url():
    try:
        logger.info("Generating LinkedIn auth URL")
        state = str(uuid.uuid4())
        auth_url = await linkedin_service.get_auth_url(state)
        if not auth_url:
            logger.error("LinkedInService.get_auth_url returned empty or invalid URL")
            raise HTTPException(status_code=500, detail="Failed to generate LinkedIn auth URL: Empty URL returned")
        logger.info(f"Generated LinkedIn auth URL with state: {state}")
        return {"authUrl": auth_url, "state": state}
    except Exception as e:
        logger.error(f"Error generating LinkedIn auth URL: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate LinkedIn auth URL: Server error.")


@router.get("/callback", include_in_schema=False)
async def linkedin_callback(
        request: Request,
        code: str = Query(...),
        state: str = Query(None),
        error: str = Query(None),
        error_description: str = Query(None)
):
    try:
        if error:
            logger.error(f"LinkedIn callback error: {error} - {error_description}")
            error_message = f"LinkedIn authentication failed: {error_description or error}"
            return RedirectResponse(url=f"{FRONTEND_REDIRECT_URI}?linkedin_error={error_message}")

        query_params = dict(request.query_params)
        account_type = query_params.get('account_type', 'personal')

        logger.info(f"LinkedIn callback with code: {code}, state: {state}, account_type (from query): {account_type}")

        token_data = await linkedin_service.exchange_code_for_token(code)
        access_token = token_data["access_token"]

        profile_data = await linkedin_service.get_user_profile(access_token)
        logger.info(f"LinkedIn profile data: {profile_data}")

        user_id_to_associate = "current_user_id"  # FIXME: This MUST be the actual authenticated user's ID from your system

        connected_account_data = {
            "user_id": user_id_to_associate,
            "platform": SocialPlatform.LINKEDIN.value,
            "name": profile_data.get("name"),
            "email": profile_data.get("email"),
            "profile_picture": profile_data.get("picture"),
            "access_token": access_token,
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600)),
            "account_id_on_platform": profile_data.get("sub"),
            "account_type": account_type,
            "is_active": True,
            "connected_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        await connected_accounts_collection.update_one(
            {
                "user_id": user_id_to_associate,
                "platform": SocialPlatform.LINKEDIN.value,
                "account_id_on_platform": profile_data.get("sub")
            },
            {"$set": connected_account_data},
            upsert=True
        )
        logger.info(f"LinkedIn account for user {user_id_to_associate} connected/updated successfully.")
        return RedirectResponse(url=f"{FRONTEND_REDIRECT_URI}?linkedin_connected=true")

    except Exception as e:
        logger.error(f"LinkedIn callback processing error: {str(e)}", exc_info=True)
        error_message = f"LinkedIn authentication processing failed: {str(e)}"
        from urllib.parse import quote
        return RedirectResponse(url=f"{FRONTEND_REDIRECT_URI}?linkedin_error={quote(error_message)}")


@router.get("/accounts")
async def get_connected_accounts_for_user(user_id: str = Query("current_user_id")):
    try:
        if user_id == "current_user_id":
            pass  # Placeholder for actual user ID logic

        accounts_cursor = connected_accounts_collection.find({"user_id": user_id})
        accounts = await accounts_cursor.to_list(None)

        for account in accounts:
            account["_id"] = str(account["_id"])
            if isinstance(account.get("expires_at"), datetime):
                account["expires_at"] = account["expires_at"].isoformat()
            if isinstance(account.get("connected_at"), datetime):
                account["connected_at"] = account["connected_at"].isoformat()
            if isinstance(account.get("updated_at"), datetime):
                account["updated_at"] = account["updated_at"].isoformat()

        return {"accounts": accounts}
    except Exception as e:
        logger.error(f"Error fetching accounts for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch connected accounts.")


@router.delete("/accounts/{account_db_id}", status_code=200)
async def disconnect_social_account(
        account_db_id: str,
        user_id: str = Query("current_user_id")
):
    try:
        if user_id == "current_user_id":
            pass  # Placeholder

        try:
            obj_account_db_id = ObjectId(account_db_id)
        except bson_errors.InvalidId:
            raise HTTPException(status_code=400, detail="Invalid account ID format.")

        result = await connected_accounts_collection.delete_one(
            {"_id": obj_account_db_id, "user_id": user_id}
        )

        if result.deleted_count == 0:
            account_exists_for_any_user = await connected_accounts_collection.count_documents(
                {"_id": obj_account_db_id})
            if account_exists_for_any_user > 0:
                raise HTTPException(status_code=403,
                                    detail="Account does not belong to this user or permission denied.")
            else:
                raise HTTPException(status_code=404, detail="Account not found.")

        logger.info(f"Account {account_db_id} for user {user_id} disconnected successfully.")
        return {"message": "Account disconnected successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disconnecting account {account_db_id} for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while disconnecting the account.")


@router.post("/post")
async def post_to_linkedin_platform(data: dict = Body(...)):
    try:
        user_id = data.get("user_id", "current_user_id")
        platform_account_id = data.get("account_id")
        content = data.get("content")
        image_url = data.get("image_url")

        logger.info(f"LinkedIn post request with account_id: {platform_account_id}")
        logger.info(f"Content: {content}")
        logger.info(f"Image URL: {image_url}")

        if not platform_account_id:
            raise HTTPException(status_code=400, detail="platform_account_id (account_id from LinkedIn) is required.")
        if not content:
            raise HTTPException(status_code=400, detail="Content is required.")

        # Fetch the specific connected account using user_id and platform_account_id
        account = await connected_accounts_collection.find_one({
            "user_id": user_id,
            "account_id_on_platform": platform_account_id,
            "platform": SocialPlatform.LINKEDIN.value
        })

        if not account:
            raise HTTPException(status_code=404, detail="LinkedIn account not found for this user and platform ID.")

        access_token = account["access_token"]
        # Token refresh logic
        if isinstance(account.get("expires_at"), datetime) and account["expires_at"] < datetime.utcnow():
            if not account.get("refresh_token"):
                raise HTTPException(status_code=401,
                                    detail="Access token expired and no refresh token available. Please reconnect.")

            logger.info(f"Refreshing token for account {platform_account_id}")
            new_tokens = await linkedin_service.refresh_token(account["refresh_token"])
            if not new_tokens:
                raise HTTPException(status_code=401, detail="Token refresh failed. Please reconnect.")

            access_token = new_tokens["access_token"]
            update_data = {
                "access_token": access_token,
                "expires_at": datetime.utcnow() + timedelta(seconds=new_tokens.get("expires_in", 3600)),
                "updated_at": datetime.utcnow()
            }
            if "refresh_token" in new_tokens:
                update_data["refresh_token"] = new_tokens["refresh_token"]

            await connected_accounts_collection.update_one(
                {"_id": account["_id"]},
                {"$set": update_data}
            )
            logger.info(f"Token refreshed and updated for account {platform_account_id}")

        # Determine user URN for posting
        author_urn = ""
        if account["account_type"] == "personal":
            author_urn = f"urn:li:person:{account['account_id_on_platform']}"
        elif account["account_type"] == "company":
            author_urn = f"urn:li:organization:{account['account_id_on_platform']}"
        else:
            raise HTTPException(status_code=400, detail=f"Unknown account type: {account['account_type']}")

        # Log information before posting
        logger.info(f"Creating LinkedIn post for {author_urn}")
        logger.info(f"With content: {content}")
        logger.info(f"Image URL: {image_url}")

        post_id = await linkedin_service.create_post(access_token, author_urn, content, image_url)
        logger.info(f"Successfully posted to LinkedIn with post_id: {post_id}")

        return {"success": True, "post_id": post_id, "message": "Successfully posted to LinkedIn."}

    except HTTPException as he:
        # Re-raise HTTP exceptions with the original status code and detail
        logger.error(f"HTTP error in LinkedIn post: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"Error posting to LinkedIn: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to post to LinkedIn: {str(e)}")