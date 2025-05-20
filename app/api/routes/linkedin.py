# linkedin.py (using the second, more complete version you provided as a base)
import logging
from fastapi import APIRouter, HTTPException, Request, Query, Body
from fastapi.responses import RedirectResponse  # Removed JSONResponse as it wasn't used directly here for responses
from datetime import datetime, timedelta
from app.services.linkedin_service import LinkedInService  # Make sure this path is correct
from app.database import connected_accounts_collection, users_collection  # Make sure this path is correct
from app.models.user import \
    SocialPlatform  # Make sure this path is correct, ConnectedAccount model not directly used here
from bson import ObjectId, errors as bson_errors  # Import bson_errors for specific exception handling
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
linkedin_service = LinkedInService()

FRONTEND_REDIRECT_URI = os.getenv("FRONTEND_REDIRECT_URI",
                                  "http://localhost:5173/social-dashboard")  # Default if not set


@router.get("/auth-url")
async def get_linkedin_auth_url():
    try:
        logger.info("Generating LinkedIn auth URL")
        # For debugging, ensure these are loaded:
        # logger.info(f"Using client_id: {os.getenv('LINKEDIN_CLIENT_ID')}")
        # logger.info(f"Using redirect_uri: {os.getenv('LINKEDIN_REDIRECT_URI')}")

        state = str(
            uuid.uuid4())  # This state should be stored (e.g., in session or short-lived DB entry) and verified in callback
        auth_url = await linkedin_service.get_auth_url(state)
        if not auth_url:
            logger.error("LinkedInService.get_auth_url returned empty or invalid URL")
            raise HTTPException(status_code=500, detail="Failed to generate LinkedIn auth URL: Empty URL returned")
        logger.info(f"Generated LinkedIn auth URL with state: {state}")
        # logger.info(f"Full auth URL: {auth_url}") # Be careful logging full URLs if they contain sensitive temp info
        return {"authUrl": auth_url, "state": state}
    except Exception as e:
        logger.error(f"Error generating LinkedIn auth URL: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate LinkedIn auth URL: Server error.")


@router.get("/callback", include_in_schema=False)
async def linkedin_callback(
        request: Request,
        code: str = Query(...),
        state: str = Query(None),  # Received state from LinkedIn
        error: str = Query(None),  # LinkedIn might return an error
        error_description: str = Query(None)  # Description for the error
        # account_type: str = Query("personal") # This was passed from frontend to LinkedIn, then back. Let's retrieve it from state or another secure mechanism.
        # For now, if LinkedIn doesn't echo it, we need to store it with the `state` before redirect.
        # A common practice: store { 'state_key': {'account_type': 'personal', 'user_id': 'actual_user_id'} }
):
    try:
        if error:
            logger.error(f"LinkedIn callback error: {error} - {error_description}")
            error_message = f"LinkedIn authentication failed: {error_description or error}"
            return RedirectResponse(url=f"{FRONTEND_REDIRECT_URI}?linkedin_error={error_message}")

        # TODO: Validate the 'state' parameter here against a stored value associated with the user's session
        # to prevent CSRF attacks. If state is invalid, raise HTTPException.
        # For example:
        # stored_state_info = await get_stored_state_info(state) # Fetch from Redis, session, etc.
        # if not stored_state_info:
        #     raise HTTPException(status_code=400, detail="Invalid state parameter or state expired.")
        # account_type = stored_state_info.get("account_type", "personal")
        # actual_user_id = stored_state_info.get("user_id") # Get the actual user ID

        # For now, we'll grab account_type from query if LinkedIn passes it through, or default
        # The frontend sends `account_type` in the initial auth URL construction.
        # LinkedIn standard flow does not guarantee to pass extra params back other than code & state.
        # The state parameter is the correct place to encode such info or a key to retrieve it.
        # For this example, let's assume account_type is part of the state or needs to be determined post-connection.
        # For now, let's hardcode for simplicity or assume it's "personal" if not derivable.
        # This part needs a robust solution for `account_type` and `user_id`.
        query_params = dict(request.query_params)
        account_type = query_params.get('account_type',
                                        'personal')  # This is NOT standard from LinkedIn, but if frontend put it there.

        logger.info(f"LinkedIn callback with code: {code}, state: {state}, account_type (from query): {account_type}")

        token_data = await linkedin_service.exchange_code_for_token(code)
        access_token = token_data["access_token"]

        profile_data = await linkedin_service.get_user_profile(
            access_token)  # Fetches name, email, picture, sub (LinkedIn ID)
        logger.info(f"LinkedIn profile data: {profile_data}")

        user_id_to_associate = "current_user_id"  # FIXME: This MUST be the actual authenticated user's ID from your system

        connected_account_data = {
            "user_id": user_id_to_associate,  # Store the app's user ID
            "platform": SocialPlatform.LINKEDIN.value,
            "name": profile_data.get("name"),
            "email": profile_data.get("email"),
            "profile_picture": profile_data.get("picture"),
            "access_token": access_token,
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600)),  # Use expires_at
            "account_id_on_platform": profile_data.get("sub"),  # LinkedIn's unique ID for the user/page
            "account_type": account_type,  # 'personal' or 'company'
            "is_active": True,
            "connected_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Upsert the account information
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
        # Ensure error_message is URL-safe if it contains special characters.
        from urllib.parse import quote
        return RedirectResponse(url=f"{FRONTEND_REDIRECT_URI}?linkedin_error={quote(error_message)}")


@router.get("/accounts")
async def get_connected_accounts_for_user(user_id: str = Query("current_user_id")):  # Get user_id from query
    try:
        if user_id == "current_user_id":  # FIXME: Replace with actual user ID from auth
            pass  # Placeholder for actual user ID logic

        accounts_cursor = connected_accounts_collection.find({"user_id": user_id})
        accounts = await accounts_cursor.to_list(None)

        for account in accounts:
            account["_id"] = str(account["_id"])  # This is the DB's unique ID for the connection record
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


# ADDED/UPDATED DELETE Endpoint
@router.delete("/accounts/{account_db_id}", status_code=200)
async def disconnect_social_account(
        account_db_id: str,
        user_id: str = Query("current_user_id")  # Get user_id from query parameter
):
    try:
        if user_id == "current_user_id":  # FIXME: Replace with actual user ID from auth
            pass  # Placeholder

        try:
            obj_account_db_id = ObjectId(account_db_id)
        except bson_errors.InvalidId:
            raise HTTPException(status_code=400, detail="Invalid account ID format.")

        # Ensure the account belongs to the user trying to delete it for security
        result = await connected_accounts_collection.delete_one(
            {"_id": obj_account_db_id, "user_id": user_id}
        )

        if result.deleted_count == 0:
            # Check if account exists at all to give a more specific error
            account_exists_for_any_user = await connected_accounts_collection.count_documents(
                {"_id": obj_account_db_id})
            if account_exists_for_any_user > 0:
                raise HTTPException(status_code=403,
                                    detail="Account does not belong to this user or permission denied.")
            else:
                raise HTTPException(status_code=404, detail="Account not found.")

        # Optional: If you also store connected accounts in a list within the main user document in `users_collection`
        # await users_collection.update_one(
        #     {"app_user_id_field": user_id},
        #     {"$pull": {"connected_accounts_array_field": {"_id": obj_account_db_id}}}
        # )

        logger.info(f"Account {account_db_id} for user {user_id} disconnected successfully.")
        return {"message": "Account disconnected successfully"}
    except HTTPException:  # Re-raise known HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error disconnecting account {account_db_id} for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while disconnecting the account.")


@router.post("/post")
async def post_to_linkedin_platform(
        # Expecting a JSON body, define with Pydantic model for validation & clarity
        # For now, using dict from Body(...)
        data: dict = Body(...)
):
    try:
        user_id = data.get("user_id", "current_user_id")  # FIXME
        platform_account_id = data.get("account_id")  # This is LinkedIn's ID for the user/page (profile_data.sub)
        content = data.get("content")
        image_url = data.get("image_url")  # Optional

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
            if "refresh_token" in new_tokens:  # LinkedIn might issue a new refresh token
                update_data["refresh_token"] = new_tokens["refresh_token"]

            await connected_accounts_collection.update_one(
                {"_id": account["_id"]},
                {"$set": update_data}
            )
            logger.info(f"Token refreshed and updated for account {platform_account_id}")

        # Determine user URN for posting
        # The platform_account_id is the 'sub' from LinkedIn (e.g., "XyZ123AbC")
        # For personal profiles: urn:li:person:{personID}
        # For Organization/Company pages: urn:li:organization:{organizationID} or urn:li:company:{companyID}
        # The `account_id_on_platform` should be the actual ID part.
        author_urn = ""
        if account["account_type"] == "personal":
            author_urn = f"urn:li:person:{account['account_id_on_platform']}"
        elif account["account_type"] == "company":  # Or "organization"
            # For company pages, the 'sub' might be the URN of the admin, not the page itself.
            # You might need to fetch organization URNs the user administers after connection.
            # This part is complex and depends on LinkedIn API version and scopes.
            # Assuming `account_id_on_platform` is the company ID for company type.
            author_urn = f"urn:li:organization:{account['account_id_on_platform']}"
        else:
            raise HTTPException(status_code=400, detail=f"Unknown account type: {account['account_type']}")

        post_id = await linkedin_service.create_post(access_token, author_urn, content, image_url)
        return {"success": True, "post_id": post_id, "message": "Successfully posted to LinkedIn."}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error posting to LinkedIn: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to post to LinkedIn: {str(e)}")