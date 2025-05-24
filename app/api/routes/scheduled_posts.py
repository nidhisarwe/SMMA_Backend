# Backend/app/api/routes/scheduled_posts.py - FIXED WITH PROPER DATETIME HANDLING
from fastapi import APIRouter, HTTPException, Depends, status
from app.database import scheduled_posts_collection, campaign_schedules_collection
from app.api.dependencies import auth_required
from datetime import datetime, timezone
from bson import ObjectId
from typing import List, Optional
import traceback
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Helper function to ensure datetime is timezone-aware (UTC)
def ensure_utc_datetime(dt):
    """Convert datetime to UTC timezone-aware datetime"""
    if dt is None:
        return None
    
    if isinstance(dt, str):
        # Parse string to datetime
        try:
            if dt.endswith('Z'):
                dt = dt.replace('Z', '+00:00')
            elif not dt.endswith(('+00:00', 'Z')) and 'T' in dt:
                dt = dt + '+00:00'
            dt = datetime.fromisoformat(dt)
        except ValueError as e:
            logger.error(f"❌ Error parsing datetime string: {dt}, error: {e}")
            raise ValueError(f"Invalid datetime format: {dt}")
    
    if dt.tzinfo is None:
        # Naive datetime - assume UTC
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        # Convert to UTC if not already
        dt = dt.astimezone(timezone.utc)
    
    return dt

def get_current_utc():
    """Get current UTC time as timezone-aware datetime"""
    return datetime.now(timezone.utc)

@router.get("/scheduled-posts")
async def get_all_posts(current_user_id: str = Depends(auth_required)):
    """
    Get all scheduled posts for the authenticated user.
    
    Args:
        current_user_id: The authenticated user ID from Firebase token
        
    Returns:
        List of user's scheduled posts
    """
    try:
        logger.info(f"🔍 Fetching scheduled posts for user: {current_user_id}")
        
        # Find posts for the current user that are NOT from campaigns
        # Use the 'source' field to filter - only include posts with source='calendar' or no source field
        cursor = scheduled_posts_collection.find({
            "user_id": current_user_id,
            "$or": [
                {"source": "calendar"},  # Posts explicitly from calendar
                {"source": {"$exists": False}},  # Posts with no source field (backward compatibility)
                {"from_campaign_id": {"$exists": False}}  # Posts not linked to campaigns
            ]
        }).sort("scheduled_time", 1)
        posts = await cursor.to_list(length=200)
        
        logger.info(f"📊 Found {len(posts)} scheduled posts for user {current_user_id}")
        
        # Convert ObjectId to string for JSON serialization and handle datetime properly
        processed_posts = []
        for post in posts:
            # Handle datetime fields properly
            scheduled_time = post.get("scheduled_time")
            created_at = post.get("created_at")
            updated_at = post.get("updated_at")
            
            # Convert datetimes to ISO format strings for JSON response
            if isinstance(scheduled_time, datetime):
                scheduled_time = scheduled_time.isoformat()
            if isinstance(created_at, datetime):
                created_at = created_at.isoformat()
            if isinstance(updated_at, datetime):
                updated_at = updated_at.isoformat()
            
            processed_post = {
                "id": str(post["_id"]),
                "caption": post.get("caption", post.get("content", "")),
                "content": post.get("content", post.get("caption", "")),
                "image_url": post.get("image_url"),
                "image_urls": post.get("image_urls", [post.get("image_url")] if post.get("image_url") else []),
                "platform": post.get("platform", "unknown"),
                "scheduled_time": scheduled_time,
                "status": post.get("status", "scheduled"),
                "is_carousel": post.get("is_carousel", False),
                "user_id": post.get("user_id"),
                "created_at": created_at,
                "updated_at": updated_at,
                "tags": post.get("tags", []),
                "assigned_to": post.get("assigned_to"),
                "theme": post.get("theme", ""),
                "title": post.get("title", ""),
                "call_to_action": post.get("call_to_action", "")
            }
            processed_posts.append(processed_post)
        
        # Return in the format expected by frontend
        return {"posts": processed_posts}
        
    except Exception as e:
        logger.error(f"❌ Error getting posts for user {current_user_id}: {e}")
        traceback_str = traceback.format_exc()
        logger.error(f"Full traceback: {traceback_str}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching posts: {str(e)}"
        )

@router.get("/scheduled-posts-stats/")
async def get_scheduled_posts_stats(current_user_id: str = Depends(auth_required)):
    """Get statistics for scheduled posts for the authenticated user."""
    try:
        logger.info(f"📊 Getting stats for user: {current_user_id}")
        
        # Get posts for this user only
        cursor = scheduled_posts_collection.find({"user_id": current_user_id})
        posts = await cursor.to_list(length=None)
        
        total_posts = len(posts)
        by_platform = {}
        by_status = {}
        
        for post in posts:
            # Platform stats
            platform = post.get("platform", "unknown")
            by_platform[platform] = by_platform.get(platform, 0) + 1
            
            # Status stats
            status = post.get("status", "scheduled")
            by_status[status] = by_status.get(status, 0) + 1
        
        result = {
            "total_posts": total_posts,
            "by_platform": by_platform,
            "by_status": by_status
        }
        
        logger.info(f"📈 Stats for user {current_user_id}: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error getting stats for user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )

@router.post("/schedule-post/")
async def schedule_post(request_data: dict, current_user_id: str = Depends(auth_required)):
    """
    Schedule a post for future publishing with proper datetime handling.
    This endpoint handles individual post scheduling from the Calendar page.
    """
    try:
        logger.info(f"📅 Scheduling post for user {current_user_id}")
        logger.info(f"📋 Request data: {list(request_data.keys())}")
        
        # Validate required fields
        if not request_data.get("caption"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Caption is required"
            )
        
        if not request_data.get("platform"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Platform is required"
            )
        
        if not request_data.get("scheduled_time"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scheduled time is required"
            )
        
        # FIXED: Parse the scheduled time with proper timezone handling
        try:
            scheduled_time_str = request_data["scheduled_time"]
            logger.info(f"🕐 Parsing scheduled time: {scheduled_time_str}")
            
            # Ensure we get a timezone-aware datetime in UTC
            scheduled_datetime = ensure_utc_datetime(scheduled_time_str)
            logger.info(f"✅ Parsed scheduled time: {scheduled_datetime} UTC")
            
        except ValueError as e:
            logger.error(f"❌ Time parsing error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid scheduled_time format. Expected ISO format: {str(e)}"
            )
        
        # FIXED: Check if scheduled time is in the future using timezone-aware comparison
        now_utc = get_current_utc()
        logger.info(f"🕐 Current UTC time: {now_utc}")
        logger.info(f"🕐 Scheduled UTC time: {scheduled_datetime}")
        
        if scheduled_datetime <= now_utc:
            logger.warning(f"⚠️ Scheduled time {scheduled_datetime} is in the past (now: {now_utc})")
            # Allow scheduling up to 2 minutes in the past to handle timezone/latency issues
            time_diff = (now_utc - scheduled_datetime).total_seconds()
            if time_diff > 120:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Scheduled time must be in the future. Current time: {now_utc.isoformat()}, Scheduled: {scheduled_datetime.isoformat()}"
                )
        
        # Prepare the post data
        post_data = {
            "caption": request_data["caption"],
            "content": request_data["caption"],  # Add content field for compatibility
            "image_url": request_data.get("image_url"),
            "image_urls": request_data.get("image_url") if isinstance(request_data.get("image_url"), list) else [request_data.get("image_url")] if request_data.get("image_url") else [],
            "platform": request_data["platform"].lower(),
            "scheduled_time": scheduled_datetime,  # Store as timezone-aware datetime
            "is_carousel": request_data.get("is_carousel", False),
            "user_id": current_user_id,  # Use authenticated user ID
            "status": "scheduled",
            "created_at": get_current_utc(),  # Use timezone-aware datetime
            "updated_at": get_current_utc(),  # Use timezone-aware datetime
            "tags": request_data.get("tags", []),
            "assigned_to": None,
            "theme": "",
            "title": request_data["caption"][:100] if request_data["caption"] else "",
            "call_to_action": "",
            "source": "calendar",  # Mark this post as coming from the calendar
            "from_draft_id": request_data.get("from_draft_id")  # Track if it came from a draft
        }
        
        logger.info(f"💾 Inserting post data for platform: {post_data['platform']}")
        
        # Insert into database
        result = await scheduled_posts_collection.insert_one(post_data)
        
        # Prepare response
        response_data = {
            "id": str(result.inserted_id),
            "message": "Post scheduled successfully",
            "scheduled_time": scheduled_datetime.isoformat(),
            "platform": request_data["platform"].lower(),
            "status": "scheduled",
            "caption": request_data["caption"],
            "image_url": request_data.get("image_url"),
            "is_carousel": request_data.get("is_carousel", False)
        }
        
        logger.info(f"✅ Post scheduled successfully with ID: {result.inserted_id}")
        return response_data
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"❌ Error scheduling post for user {current_user_id}: {str(e)}")
        traceback_str = traceback.format_exc()
        logger.error(f"Full traceback: {traceback_str}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule post: {str(e)}"
        )

@router.get("/scheduled-posts/{post_id}")
async def get_post_by_id(post_id: str, current_user_id: str = Depends(auth_required)):
    """
    Get a specific scheduled post by ID, ensuring it belongs to the authenticated user.
    """
    try:
        # Find the post and ensure it belongs to the current user
        post = await scheduled_posts_collection.find_one({
            "_id": ObjectId(post_id),
            "user_id": current_user_id
        })
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or you don't have permission to access it"
            )
        
        # Convert ObjectId to string and handle datetime fields
        post["id"] = str(post["_id"])
        del post["_id"]
        
        # Handle datetime serialization
        for field in ["scheduled_time", "created_at", "updated_at"]:
            if field in post and isinstance(post[field], datetime):
                post[field] = post[field].isoformat()
        
        return post
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"❌ Error getting post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the post: {str(e)}"
        )

@router.put("/scheduled-posts/{post_id}")
async def update_post(post_id: str, post_data: dict, current_user_id: str = Depends(auth_required)):
    """
    Update a scheduled post, ensuring it belongs to the authenticated user.
    """
    try:
        # Find the post and ensure it belongs to the current user
        existing_post = await scheduled_posts_collection.find_one({
            "_id": ObjectId(post_id),
            "user_id": current_user_id
        })
        
        if not existing_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or you don't have permission to update it"
            )
        
        # Prepare update data
        update_data = {
            "updated_at": get_current_utc()
        }
        
        # Update only provided fields
        if "caption" in post_data:
            update_data["caption"] = post_data["caption"]
            update_data["content"] = post_data["caption"]
        if "status" in post_data:
            update_data["status"] = post_data["status"]
        if "scheduled_time" in post_data:
            update_data["scheduled_time"] = ensure_utc_datetime(post_data["scheduled_time"])
        
        # Update the post
        await scheduled_posts_collection.update_one(
            {"_id": ObjectId(post_id), "user_id": current_user_id},
            {"$set": update_data}
        )
        
        # Return the updated post
        updated_post = await scheduled_posts_collection.find_one({
            "_id": ObjectId(post_id),
            "user_id": current_user_id
        })
        updated_post["id"] = str(updated_post["_id"])
        del updated_post["_id"]
        
        # Handle datetime serialization
        for field in ["scheduled_time", "created_at", "updated_at"]:
            if field in updated_post and isinstance(updated_post[field], datetime):
                updated_post[field] = updated_post[field].isoformat()
        
        return updated_post
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"❌ Error updating post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the post: {str(e)}"
        )

@router.delete("/scheduled-posts/{post_id}")
async def delete_post(post_id: str, current_user_id: str = Depends(auth_required)):
    """
    Delete a scheduled post, ensuring it belongs to the authenticated user.
    """
    try:
        logger.info(f"🗑️ Attempting to delete post {post_id} for user {current_user_id}")
        
        # Find and delete the post
        result = await scheduled_posts_collection.delete_one({
            "_id": ObjectId(post_id),
            "user_id": current_user_id
        })
        
        if result.deleted_count == 0:
            logger.warning(f"⚠️ Post {post_id} not found or doesn't belong to user {current_user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or you don't have permission to delete it"
            )
        
        logger.info(f"✅ Successfully deleted post {post_id}")
        return {"message": "Post deleted successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"❌ Error deleting post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the post: {str(e)}"
        )

@router.patch("/scheduled-posts/{post_id}")
async def patch_post(post_id: str, update_data: dict, current_user_id: str = Depends(auth_required)):
    """
    Partially update a scheduled post (PATCH), ensuring it belongs to the authenticated user.
    """
    try:
        logger.info(f"🔧 Patching post {post_id} for user {current_user_id}")
        
        # Check if post exists and belongs to user
        existing_post = await scheduled_posts_collection.find_one({
            "_id": ObjectId(post_id),
            "user_id": current_user_id
        })
        
        if not existing_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or you don't have permission to update it"
            )
        
        # Remove None values and prepare update
        clean_update_data = {k: v for k, v in update_data.items() if v is not None}
        
        if not clean_update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data provided for update"
            )
        
        # Handle datetime fields properly
        if "scheduled_time" in clean_update_data:
            clean_update_data["scheduled_time"] = ensure_utc_datetime(clean_update_data["scheduled_time"])
        
        # Add updated timestamp
        clean_update_data["updated_at"] = get_current_utc()
        
        # Update the post
        result = await scheduled_posts_collection.update_one(
            {"_id": ObjectId(post_id), "user_id": current_user_id},
            {"$set": clean_update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        logger.info(f"✅ Successfully patched post {post_id}")
        return {"message": "Post updated successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"❌ Error patching post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update post: {str(e)}"
        )