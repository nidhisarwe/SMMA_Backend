# app/api/routes/accounts.py
import logging
from fastapi import APIRouter, HTTPException, Body, Depends
from app.database import connected_accounts_collection
from app.api.dependencies import auth_required
from bson import ObjectId
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def get_connected_accounts(current_user_id: str = Depends(auth_required)):
    """
    Get all connected social accounts for the authenticated user ONLY.
    
    Args:
        current_user_id: The authenticated user ID from Firebase token
        
    Returns:
        List of user's connected accounts (filtered by user_id)
    """
    try:
        print(f"🔍 Fetching connected accounts for user: {current_user_id}")
        
        # Critical: Filter by user_id to ensure data isolation
        cursor = connected_accounts_collection.find({"user_id": current_user_id})
        accounts = await cursor.to_list(length=None)

        print(f"✅ Found {len(accounts)} connected accounts for user {current_user_id}")

        # Convert ObjectIds to strings for JSON serialization
        for account in accounts:
            if "_id" in account:
                account["_id"] = str(account["_id"])
            if "user_id" in account:
                account["user_id"] = str(account["user_id"])
            # Convert datetime fields for JSON serialization
            for field in ["expires_at", "connected_at", "updated_at"]:
                if field in account and isinstance(account[field], datetime):
                    account[field] = account[field].isoformat()

        return {"accounts": accounts}
        
    except Exception as e:
        logger.error(f"Error fetching connected accounts for user {current_user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch connected accounts: {str(e)}")

@router.delete("/{account_id}")
async def disconnect_account(account_id: str, current_user_id: str = Depends(auth_required)):
    """
    Disconnect a social account, ensuring it belongs to the authenticated user.
    
    Args:
        account_id: The ID of the account to disconnect
        current_user_id: The authenticated user ID from Firebase token
        
    Returns:
        Success message
    """
    try:
        print(f"🔄 Disconnecting account {account_id} for user {current_user_id}")
        
        # Validate the account_id can be converted to ObjectId
        try:
            account_obj_id = ObjectId(account_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid account ID format")

        # Critical: Delete only if the account belongs to the current user
        result = await connected_accounts_collection.delete_one({
            "_id": account_obj_id,
            "user_id": current_user_id  # Ensure user owns this account
        })

        if result.deleted_count == 0:
            # Check if account exists for any user (for better error message)
            account_exists = await connected_accounts_collection.find_one({"_id": account_obj_id})
            if account_exists:
                raise HTTPException(
                    status_code=403, 
                    detail="Account does not belong to this user or permission denied"
                )
            else:
                raise HTTPException(status_code=404, detail="Account not found")

        print(f"✅ Account {account_id} disconnected successfully for user {current_user_id}")
        return {"success": True, "message": "Account disconnected successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error disconnecting account {account_id} for user {current_user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to disconnect account: {str(e)}")