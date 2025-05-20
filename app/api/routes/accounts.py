# # backend/app/api/routes/accounts.py
# from fastapi import APIRouter, HTTPException
# from bson import ObjectId
# from app.database import connected_accounts_collection
#
# router = APIRouter()
#
#
# @router.get("/")
# async def get_all_connected_accounts(user_id: str):
#     try:
#         accounts = await connected_accounts_collection.find(
#             {"user_id": ObjectId(user_id)}
#         ).to_list(None)
#
#         for account in accounts:
#             account["_id"] = str(account["_id"])
#             account["user_id"] = str(account["user_id"])
#
#         return {"accounts": accounts}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @router.delete("/{account_id}")
# async def disconnect_account(user_id: str, account_id: str):
#     try:
#         result = await connected_accounts_collection.delete_one({
#             "user_id": ObjectId(user_id),
#             "_id": ObjectId(account_id)
#         })
#
#         if result.deleted_count == 0:
#             raise HTTPException(status_code=404, detail="Account not found")
#
#         return {"success": True}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
# accounts.py
import logging
from fastapi import APIRouter, HTTPException, Body
from app.database import connected_accounts_collection
from bson import ObjectId

# Fix logger name
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # Changed from _name_ to __name__

router = APIRouter()


@router.get("/")
async def get_connected_accounts(user_id: str = "current_user_id"):
    """
    Get all connected social accounts for a user
    """
    try:
        # Properly use Motor's async find operation
        cursor = connected_accounts_collection.find({"user_id": user_id})
        # Use to_list with Motor's cursor
        accounts = await cursor.to_list(length=None)

        # Convert ObjectIds to strings for JSON serialization
        for account in accounts:
            if "_id" in account:
                account["_id"] = str(account["_id"])
            if "user_id" in account:
                account["user_id"] = str(account["user_id"])

        return {"accounts": accounts}
    except Exception as e:
        logger.error(f"Error fetching connected accounts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{account_id}")
async def disconnect_account(account_id: str, data: dict = Body(default={})):
    """
    Disconnect a social account
    """
    try:
        user_id = data.get("user_id", "current_user_id")

        # Validate the account_id can be converted to ObjectId
        try:
            account_obj_id = ObjectId(account_id)
        except:
            # If it's not a valid ObjectId, it might be a string ID
            account_obj_id = account_id

        # Try to find and delete the account
        result = await connected_accounts_collection.delete_one({
            "_id": account_obj_id,
            "user_id": user_id
        })

        if result.deleted_count == 0:
            # If no document was deleted with _id, try with account_id field
            result = await connected_accounts_collection.delete_one({
                "account_id": account_id,
                "user_id": user_id
            })

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Account not found or already disconnected")

        return {"success": True, "message": "Account disconnected successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error disconnecting account: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
