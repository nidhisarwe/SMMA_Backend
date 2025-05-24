# app/api/routes/drafts.py
from fastapi import APIRouter, HTTPException, status, Query, Request, Depends
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional, Union
from app.database import drafts_collection
from app.api.dependencies import auth_required
import logging
import re
from bson import ObjectId

router = APIRouter()

logger = logging.getLogger(__name__)
logger.info("Loading drafts.py with user isolation and authentication")

class DraftCreate(BaseModel):
    caption: str = Field(..., min_length=1, max_length=2200)
    platform: str = Field(..., pattern=r"^(instagram|facebook|twitter|linkedin)$")
    image_url: Optional[Union[str, List[str]]] = None
    prompt: Optional[str] = Field(None, max_length=500)
    is_carousel: bool = False

    @validator('image_url')
    def validate_image_url(cls, v, values):
        is_carousel = values.get('is_carousel', False)

        if v is None:
            return v

        if is_carousel:
            if not isinstance(v, list):
                # Try to convert single string to list if needed
                if isinstance(v, str):
                    return [v]
                raise ValueError("For carousel posts, image_url must be a list or string")

            # Ensure all items in list are strings
            return [str(url) for url in v]
        else:
            if isinstance(v, list):
                # If single post but got list, use first item
                if len(v) > 0:
                    return str(v[0])
                return None
            return str(v) if v else None

@router.post("/save-draft/", status_code=status.HTTP_201_CREATED)
async def save_draft(request: Request, draft: DraftCreate, current_user_id: str = Depends(auth_required)):
    """
    Save a draft for the authenticated user.
    
    Args:
        draft: Draft data to save
        current_user_id: The authenticated user ID from Firebase token
        
    Returns:
        Success message with draft ID
    """
    try:
        raw_body = await request.body()
        logger.info(f"Raw request body: {raw_body.decode('utf-8')}")
        
        draft_data = draft.dict()
        logger.info(f"Received draft data: {draft_data}")
        
        # Critical: Add user_id to ensure data isolation
        draft_data["user_id"] = current_user_id
        draft_data["created_at"] = datetime.utcnow()
        draft_data["updated_at"] = datetime.utcnow()
        draft_data["status"] = "draft"

        # Insert draft with user association
        result = await drafts_collection.insert_one(draft_data)
        logger.info(f"Draft saved successfully with ID: {result.inserted_id} for user: {current_user_id}")

        return {
            "status": "success",
            "message": "Draft saved successfully",
            "draft_id": str(result.inserted_id)
        }

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "status": "error",
                "message": "Validation error",
                "error": str(ve)
            }
        )
    except Exception as e:
        logger.error(f"Draft save error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to save draft",
                "error": str(e)
            }
        )

@router.get("/get-drafts/", response_model=dict)
async def get_drafts(
    current_user_id: str = Depends(auth_required),
    page: int = Query(1, ge=1), 
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get all drafts for the authenticated user.
    
    Args:
        current_user_id: The authenticated user ID from Firebase token
        page: Page number for pagination
        limit: Number of drafts per page
        
    Returns:
        Paginated list of user's drafts
    """
    try:
        logger.info(f"🔍 Fetching drafts for user: {current_user_id} (page: {page}, limit: {limit})")
        skip = (page - 1) * limit
        
        # Critical: Filter by user_id to ensure data isolation
        filter_query = {"user_id": current_user_id}
        logger.info(f"🔎 Query filter: {filter_query}")
        
        # Get total count for this user only
        total = await drafts_collection.count_documents(filter_query)
        logger.info(f"📊 Total drafts found: {total}")

        # Get drafts for this user only
        cursor = drafts_collection.find(filter_query).sort("created_at", -1).skip(skip).limit(limit)
        drafts = await cursor.to_list(length=None)
        logger.info(f"📋 Retrieved {len(drafts)} drafts")

        # Process results
        for draft in drafts:
            draft["_id"] = str(draft["_id"])
            if "created_at" in draft and isinstance(draft["created_at"], datetime):
                draft["created_at"] = draft["created_at"].isoformat()
            elif "created_at" in draft and not isinstance(draft["created_at"], str):
                draft["created_at"] = str(draft["created_at"])

        logger.info(f"Retrieved {len(drafts)} drafts for user {current_user_id}")

        # Ensure consistent response structure that matches what frontend expects
        return {
            "status": "success",
            "data": drafts,  # Keep 'data' for backward compatibility
            "drafts": drafts,  # Add 'drafts' for newer frontend versions
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
            "total_pages": (total + limit - 1) // limit  # Add total_pages for newer frontend versions
        }
        
    except Exception as e:
        logger.error(f"Get drafts error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to fetch drafts",
                "error": str(e)
            }
        )

@router.get("/drafts/{draft_id}")
async def get_draft_by_id(draft_id: str, current_user_id: str = Depends(auth_required)):
    """
    Get a specific draft by ID, ensuring it belongs to the authenticated user.
    
    Args:
        draft_id: The ID of the draft to retrieve
        current_user_id: The authenticated user ID from Firebase token
        
    Returns:
        Draft details if found and owned by the user
    """
    try:
        # Validate ObjectId format
        try:
            draft_obj_id = ObjectId(draft_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid draft ID format"
            )
        
        # Critical: Find draft with both the ID and user_id to ensure ownership
        draft = await drafts_collection.find_one({
            "_id": draft_obj_id,
            "user_id": current_user_id
        })
        
        if not draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found or you don't have permission to access it"
            )
        
        # Convert ObjectId to string for JSON serialization
        draft["id"] = str(draft.pop("_id"))
        
        return {
            "status": "success",
            "data": draft
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Get draft error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to fetch draft",
                "error": str(e)
            }
        )

@router.put("/drafts/{draft_id}")
async def update_draft(draft_id: str, draft_data: DraftCreate, current_user_id: str = Depends(auth_required)):
    """
    Update a draft, ensuring it belongs to the authenticated user.
    
    Args:
        draft_id: The ID of the draft to update
        draft_data: Updated draft data
        current_user_id: The authenticated user ID from Firebase token
        
    Returns:
        Updated draft details
    """
    try:
        # Validate ObjectId format
        try:
            draft_obj_id = ObjectId(draft_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid draft ID format"
            )
        
        # Critical: Find the draft and ensure it belongs to the current user
        existing_draft = await drafts_collection.find_one({
            "_id": draft_obj_id,
            "user_id": current_user_id
        })
        
        if not existing_draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found or you don't have permission to update it"
            )
        
        # Prepare update data
        update_data = draft_data.dict()
        update_data["updated_at"] = datetime.utcnow()
        # Ensure user_id is preserved
        update_data["user_id"] = current_user_id
        
        # Update the draft
        await drafts_collection.update_one(
            {"_id": draft_obj_id, "user_id": current_user_id},
            {"$set": update_data}
        )
        
        # Return the updated draft
        updated_draft = await drafts_collection.find_one({
            "_id": draft_obj_id,
            "user_id": current_user_id
        })
        updated_draft["id"] = str(updated_draft.pop("_id"))
        
        return {
            "status": "success",
            "message": "Draft updated successfully",
            "data": updated_draft
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Update draft error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to update draft",
                "error": str(e)
            }
        )

@router.delete("/delete-draft/{draft_id}", status_code=status.HTTP_200_OK)
async def delete_draft(draft_id: str, current_user_id: str = Depends(auth_required)):
    """
    Delete a draft, ensuring it belongs to the authenticated user.
    
    Args:
        draft_id: The ID of the draft to delete
        current_user_id: The authenticated user ID from Firebase token
        
    Returns:
        Success message
    """
    try:
        # Validate ObjectId format
        try:
            draft_obj_id = ObjectId(draft_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid draft ID format"
            )
        
        # Critical: Delete only if the draft belongs to the current user
        result = await drafts_collection.delete_one({
            "_id": draft_obj_id,
            "user_id": current_user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found or you don't have permission to delete it"
            )
        
        logger.info(f"Draft {draft_id} deleted successfully for user {current_user_id}")
        
        return {
            "status": "success",
            "message": "Draft deleted successfully"
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Delete draft error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to delete draft",
                "error": str(e)
            }
        )