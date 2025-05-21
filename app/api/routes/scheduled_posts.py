from fastapi import APIRouter, HTTPException, Body, Query, Path
from app.database import scheduled_posts_collection
from datetime import datetime
from bson import ObjectId
from typing import Dict, Any, List, Optional, Union  # Added Union
import logging
from pydantic import BaseModel, Field

router = APIRouter()
logger = logging.getLogger(__name__)


class SchedulePostRequest(BaseModel):
    caption: str
    image_url: Union[str, List[str]]  # Changed to Union
    platform: str
    scheduled_time: datetime
    is_carousel: bool = False
    user_id: str = "current_user_id"
    tags: List[str] = Field(default_factory=list)
    account_id_on_platform: Optional[str] = None  # Added
    account_type: Optional[str] = None  # Added


class UpdateScheduledPostRequest(BaseModel):
    caption: Optional[str] = None
    image_url: Optional[Union[str, List[str]]] = None  # Changed to Union
    scheduled_time: Optional[datetime] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    account_id_on_platform: Optional[str] = None  # Added
    account_type: Optional[str] = None  # Added


@router.post("/schedule-post/")
async def schedule_post(request: SchedulePostRequest):
    """
    Schedule a post to be published at a specific time
    """
    try:
        post_data = request.dict()

        # Add additional fields
        post_data["status"] = "scheduled"
        post_data["created_at"] = datetime.utcnow()

        # Ensure account_id_on_platform and account_type are included
        # Pydantic's dict() should handle this if they are in the request
        # but explicit assignment is fine if needed.
        # post_data["account_id_on_platform"] = request.account_id_on_platform
        # post_data["account_type"] = request.account_type

        logger.info(f"Scheduling post data: {post_data}")

        # Insert into the database
        result = await scheduled_posts_collection.insert_one(post_data)

        logger.info(f"Post scheduled successfully with ID: {result.inserted_id}")

        return {
            "message": "Post scheduled successfully",
            "id": str(result.inserted_id),
            "scheduled_time": post_data["scheduled_time"].isoformat(),
            "account_id_on_platform": post_data.get("account_id_on_platform")
        }
    except Exception as e:
        logger.error(f"Failed to schedule post: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule post: {str(e)}")


@router.get("/scheduled-posts/")
async def get_scheduled_posts(user_id: str = Query("current_user_id")):
    """
    Get all scheduled posts for a user
    """
    try:
        logger.info(f"Fetching scheduled posts for user_id: {user_id}")
        cursor = scheduled_posts_collection.find({"user_id": user_id})
        posts = await cursor.to_list(length=None)
        logger.info(f"Found {len(posts)} posts for user_id: {user_id}")

        # Format the response
        formatted_posts = []
        for post in posts:
            post_id = str(post.pop("_id"))
            post["id"] = post_id

            # Format dates to ISO strings
            for field in ["scheduled_time", "created_at", "published_at", "attempted_at"]:
                if field in post and isinstance(post[field], datetime):
                    post[field] = post[field].isoformat()

            # Ensure account_id_on_platform is included if present
            if "account_id_on_platform" not in post:
                post["account_id_on_platform"] = None  # Default if not present
            if "account_type" not in post:
                post["account_type"] = None

            formatted_posts.append(post)

        # logger.debug(f"Formatted posts: {formatted_posts}")
        return formatted_posts
    except Exception as e:
        logger.error(f"Failed to fetch scheduled posts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch scheduled posts: {str(e)}")


@router.get("/scheduled-posts/{post_id}")
async def get_scheduled_post(post_id: str = Path(...)):
    """
    Get a specific scheduled post by ID
    """
    try:
        # Skip this endpoint if "stats" is in the path
        if post_id == "stats":  # This handles the old stats path if hit directly
            raise HTTPException(status_code=404, detail="Stats endpoint is now /api/scheduled-posts-stats/")

        post = await scheduled_posts_collection.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Format the response
        post["id"] = str(post.pop("_id"))

        # Format dates to ISO strings
        for field in ["scheduled_time", "created_at", "published_at", "attempted_at"]:
            if field in post and isinstance(post[field], datetime):
                post[field] = post[field].isoformat()

        if "account_id_on_platform" not in post:
            post["account_id_on_platform"] = None
        if "account_type" not in post:
            post["account_type"] = None

        return post
    except HTTPException:
        raise
    except bson.errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid post ID format.")
    except Exception as e:
        logger.error(f"Failed to fetch scheduled post {post_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch scheduled post: {str(e)}")


@router.patch("/scheduled-posts/{post_id}")
async def update_scheduled_post(post_id: str, update_data: UpdateScheduledPostRequest):
    """
    Update a scheduled post
    """
    try:
        data_dict = update_data.dict(exclude_unset=True)
        if not data_dict:
            raise HTTPException(status_code=400, detail="No update data provided")

        # Add updated_at timestamp
        data_dict["updated_at"] = datetime.utcnow()

        # Update the post
        result = await scheduled_posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": data_dict}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Post not found")

        return {
            "message": "Post updated successfully",
            "id": post_id
        }
    except HTTPException:
        raise
    except bson.errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid post ID format.")
    except Exception as e:
        logger.error(f"Failed to update scheduled post {post_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update scheduled post: {str(e)}")


@router.delete("/scheduled-posts/{post_id}")
async def delete_scheduled_post(post_id: str):
    """
    Delete a scheduled post
    """
    try:
        result = await scheduled_posts_collection.delete_one({"_id": ObjectId(post_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Post not found")

        return {"message": "Post deleted successfully"}
    except HTTPException:
        raise
    except bson.errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid post ID format.")
    except Exception as e:
        logger.error(f"Failed to delete scheduled post {post_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete scheduled post: {str(e)}")


# This is the specific endpoint for stats
@router.get("/scheduled-posts-stats/")
async def get_scheduled_posts_stats(user_id: str = Query("current_user_id")):
    """
    Get statistics about scheduled posts
    """
    try:
        # Count total posts
        total_posts = await scheduled_posts_collection.count_documents({"user_id": user_id})

        # Count posts by platform
        pipeline_platform = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$platform", "count": {"$sum": 1}}}
        ]
        platform_cursor = scheduled_posts_collection.aggregate(pipeline_platform)
        platforms = {}
        async for item in platform_cursor:
            platforms[item["_id"]] = item["count"]

        # Count posts by status
        pipeline_status = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        status_cursor = scheduled_posts_collection.aggregate(pipeline_status)
        statuses = {}
        async for item in status_cursor:
            statuses[item["_id"]] = item["count"]

        return {
            "total_posts": total_posts,
            "by_platform": platforms,
            "by_status": statuses
        }
    except Exception as e:
        logger.error(f"Failed to fetch scheduled posts stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch scheduled posts stats: {str(e)}")