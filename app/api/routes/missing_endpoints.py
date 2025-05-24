# Backend/app/api/routes/missing_endpoints.py - UPDATED WITH ENHANCED FEATURES
from fastapi import APIRouter, HTTPException, Depends
from app.api.dependencies import auth_required
from app.database import campaign_schedules_collection, scheduled_posts_collection
from datetime import datetime
from bson import ObjectId
import traceback

router = APIRouter()

@router.get("/get-campaigns")
async def get_campaigns(current_user_id: str = Depends(auth_required)):
    """
    Get all campaigns for the authenticated user.
    This endpoint is called by CreatePost.jsx
    """
    try:
        print(f"🔍 Fetching campaigns for user: {current_user_id}")
        
        # Find campaigns for the current user
        cursor = campaign_schedules_collection.find({"user_id": current_user_id}).sort("created_at", -1)
        campaigns = await cursor.to_list(length=100)
        
        # Convert ObjectId to string for JSON serialization
        for campaign in campaigns:
            campaign["_id"] = str(campaign["_id"])
            if "posts" in campaign:
                for post in campaign["posts"]:
                    if "_id" in post:
                        post["_id"] = str(post["_id"])
        
        print(f"✅ Found {len(campaigns)} campaigns for user")
        return campaigns
        
    except Exception as e:
        print(f"❌ Error fetching campaigns: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch campaigns: {str(e)}"
        )

@router.get("/get-campaign/{campaign_id}")
async def get_campaign_by_id(campaign_id: str, current_user_id: str = Depends(auth_required)):
    """
    Get a specific campaign by ID for the authenticated user.
    This endpoint is called by CreatePost.jsx
    """
    try:
        print(f"🔍 Fetching campaign {campaign_id} for user: {current_user_id}")
        
        # Validate ObjectId format
        try:
            campaign_obj_id = ObjectId(campaign_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid campaign ID format")
        
        # Find campaign with user check
        campaign = await campaign_schedules_collection.find_one({
            "_id": campaign_obj_id,
            "user_id": current_user_id
        })
        
        if not campaign:
            raise HTTPException(
                status_code=404, 
                detail="Campaign not found or you don't have permission to access it"
            )
        
        # Convert ObjectId to string
        campaign["_id"] = str(campaign["_id"])
        
        # Get posts for this campaign
        cursor = scheduled_posts_collection.find({
            "campaign_id": campaign_id,
            "user_id": current_user_id
        }).sort("post_index", 1)
        
        posts = await cursor.to_list(length=100)
        
        # Convert ObjectIds in posts
        for post in posts:
            post["_id"] = str(post["_id"])
        
        campaign["posts"] = posts
        
        print(f"✅ Found campaign with {len(posts)} posts")
        return campaign
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Error fetching campaign: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch campaign: {str(e)}"
        )

@router.get("/scheduled-posts-stats/")
async def get_scheduled_posts_stats(current_user_id: str = Depends(auth_required)):
    """
    Get statistics for scheduled posts for the authenticated user.
    Enhanced version with platform and detailed status breakdown.
    """
    try:
        print(f"🔍 Fetching scheduled posts stats for user: {current_user_id}")
        
        # Get all posts for the user
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
        
        stats = {
            "total_posts": total_posts,
            "by_platform": by_platform,
            "by_status": by_status,
            # Legacy compatibility
            "scheduled_posts": by_status.get("scheduled", 0),
            "published_posts": by_status.get("published", 0),
            "draft_posts": by_status.get("draft", 0)
        }
        
        print(f"✅ Stats calculated: {stats}")
        return stats
        
    except Exception as e:
        print(f"❌ Error fetching stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )

@router.get("/scheduled-posts")
async def get_user_scheduled_posts(current_user_id: str = Depends(auth_required)):
    """
    Get all scheduled posts for the authenticated user.
    """
    try:
        print(f"🔍 Fetching scheduled posts for user: {current_user_id}")
        
        cursor = scheduled_posts_collection.find({"user_id": current_user_id}).sort("scheduled_time", 1)
        posts = await cursor.to_list(length=200)
        
        # Convert ObjectId to string and format dates
        for post in posts:
            post["id"] = str(post.pop("_id"))
            if isinstance(post.get("created_at"), datetime):
                post["created_at"] = post["created_at"].isoformat()
            if isinstance(post.get("updated_at"), datetime):
                post["updated_at"] = post["updated_at"].isoformat()
            if isinstance(post.get("scheduled_time"), datetime):
                post["scheduled_time"] = post["scheduled_time"].isoformat()
        
        print(f"✅ Found {len(posts)} scheduled posts")
        return {"posts": posts}
        
    except Exception as e:
        print(f"❌ Error fetching scheduled posts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scheduled posts: {str(e)}"
        )

@router.get("/team-members")
async def get_team_members():
    """
    Get team members (mock data for now).
    In a real application, this would fetch from a teams/users database.
    """
    try:
        print("🔍 Fetching team members (mock data)")
        
        # Mock team members data
        team_members = [
            {"id": "1", "username": "user1", "name": "John Doe", "email": "john@example.com", "role": "Content Creator"},
            {"id": "2", "username": "user2", "name": "Jane Smith", "email": "jane@example.com", "role": "Social Media Manager"},
            {"id": "3", "username": "user3", "name": "Bob Johnson", "email": "bob@example.com", "role": "Marketing Lead"},
            {"id": "4", "username": "user4", "name": "Alice Brown", "email": "alice@example.com", "role": "Designer"},
            {"id": "5", "username": "user5", "name": "Mike Wilson", "email": "mike@example.com", "role": "Analyst"}
        ]
        
        print(f"✅ Returning {len(team_members)} team members")
        return team_members
        
    except Exception as e:
        print(f"❌ Error fetching team members: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch team members: {str(e)}")

@router.post("/schedule-post/")
async def schedule_post(request: dict, current_user_id: str = Depends(auth_required)):
    """
    Schedule a single post for the authenticated user.
    Enhanced version with proper user isolation.
    """
    try:
        print(f"🔍 Scheduling post for user: {current_user_id}")
        
        # Validate required fields
        required_fields = ["caption", "platform", "scheduled_time"]
        for field in required_fields:
            if field not in request:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )
        
        post_data = {
            "caption": request.get("caption"),
            "content": request.get("caption"),  # Alias for compatibility
            "image_url": request.get("image_url"),
            "image_urls": request.get("image_url"),  # Alias for compatibility
            "platform": request.get("platform"),
            "scheduled_time": request.get("scheduled_time"),
            "status": request.get("status", "scheduled"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_carousel": request.get("is_carousel", False),
            "user_id": current_user_id,  # Critical: Associate with authenticated user
            "tags": request.get("tags", []),
            "title": request.get("title", ""),
            "theme": request.get("theme", ""),
            "call_to_action": request.get("call_to_action", ""),
            "assigned_to": request.get("assigned_to"),
            "post_type": request.get("post_type", "text")
        }

        # Insert the post
        result = await scheduled_posts_collection.insert_one(post_data)
        
        print(f"✅ Post scheduled successfully with ID: {result.inserted_id}")
        return {
            "message": "Post scheduled successfully",
            "id": str(result.inserted_id),
            "success": True
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Error scheduling post: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to schedule post: {str(e)}")

@router.delete("/scheduled-posts/{post_id}")
async def delete_scheduled_post(post_id: str, current_user_id: str = Depends(auth_required)):
    """
    Delete a scheduled post, ensuring it belongs to the authenticated user.
    """
    try:
        print(f"🔍 Deleting post {post_id} for user: {current_user_id}")
        
        # Validate ObjectId format
        try:
            post_obj_id = ObjectId(post_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid post ID format")
        
        # Delete post with user check
        result = await scheduled_posts_collection.delete_one({
            "_id": post_obj_id,
            "user_id": current_user_id  # Ensure user owns this post
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404, 
                detail="Post not found or you don't have permission to delete it"
            )
        
        print(f"✅ Post deleted successfully")
        return {"message": "Post deleted successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Error deleting post: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete post: {str(e)}")

@router.patch("/scheduled-posts/{post_id}")
async def update_scheduled_post(post_id: str, update_data: dict, current_user_id: str = Depends(auth_required)):
    """
    Update a scheduled post, ensuring it belongs to the authenticated user.
    """
    try:
        print(f"🔍 Updating post {post_id} for user: {current_user_id}")
        
        # Validate ObjectId format
        try:
            post_obj_id = ObjectId(post_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid post ID format")
        
        # Remove None values from update data
        update_data = {k: v for k, v in update_data.items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="No data provided for update")

        # Add updated timestamp
        update_data["updated_at"] = datetime.utcnow()

        # Update post with user check
        result = await scheduled_posts_collection.update_one(
            {
                "_id": post_obj_id,
                "user_id": current_user_id  # Ensure user owns this post
            },
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=404, 
                detail="Post not found or you don't have permission to update it"
            )

        print(f"✅ Post updated successfully")
        return {"message": "Post updated successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Error updating post: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update post: {str(e)}")

@router.get("/scheduled-posts/")
async def legacy_get_scheduled_posts(current_user_id: str = Depends(auth_required)):
    """
    Legacy endpoint for backward compatibility.
    Returns scheduled posts in the old format.
    """
    try:
        print(f"🔍 Legacy: Fetching scheduled posts for user: {current_user_id}")
        
        cursor = scheduled_posts_collection.find({"user_id": current_user_id})
        scheduled_posts = await cursor.to_list(length=None)

        posts_list = [
            {
                "id": str(post["_id"]),
                "caption": post.get("caption", ""),
                "content": post.get("content", post.get("caption", "")),
                "image_url": post.get("image_url"),
                "image_urls": post.get("image_urls", post.get("image_url")),
                "platform": post.get("platform"),
                "scheduled_time": post.get("scheduled_time"),
                "status": post.get("status", "scheduled"),
                "created_at": post.get("created_at"),
                "is_carousel": post.get("is_carousel", False),
                "user_id": post.get("user_id"),
                "tags": post.get("tags", []),
                "assigned_to": post.get("assigned_to"),
                "theme": post.get("theme", ""),
                "title": post.get("title", ""),
                "call_to_action": post.get("call_to_action", "")
            }
            for post in scheduled_posts
        ]
        
        print(f"✅ Legacy: Returning {len(posts_list)} posts")
        return posts_list
        
    except Exception as e:
        print(f"❌ Legacy: Error fetching scheduled posts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch scheduled posts: {str(e)}")