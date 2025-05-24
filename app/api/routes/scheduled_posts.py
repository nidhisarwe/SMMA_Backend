from fastapi import APIRouter, HTTPException, Depends, status
from app.database import scheduled_posts_collection, campaign_schedules_collection
from app.api.dependencies import auth_required
from datetime import datetime
from bson import ObjectId
from typing import List, Optional
import traceback

router = APIRouter()


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
        # Find all posts for the current user
        cursor = scheduled_posts_collection.find({"user_id": current_user_id})
        posts = await cursor.to_list(length=100)
        
        # Convert ObjectId to string for JSON serialization
        for post in posts:
            post["id"] = str(post["_id"])
            post["campaign_id"] = str(post["campaign_id"])
            del post["_id"]
        
        return {"posts": posts}
    except Exception as e:
        print(f"Error getting posts: {e}")
        traceback_str = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching posts: {str(e)}"
        )


@router.get("/scheduled-posts/{post_id}")
async def get_post_by_id(post_id: str, current_user_id: str = Depends(auth_required)):
    """
    Get a specific scheduled post by ID, ensuring it belongs to the authenticated user.
    
    Args:
        post_id: The ID of the post to retrieve
        current_user_id: The authenticated user ID from Firebase token
        
    Returns:
        Post details if found and owned by the user
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
        
        # Convert ObjectId to string for JSON serialization
        post["id"] = str(post["_id"])
        post["campaign_id"] = str(post["campaign_id"])
        del post["_id"]
        
        return post
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error getting post: {e}")
        traceback_str = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the post: {str(e)}"
        )


@router.post("/scheduled-posts")
async def create_post(post_data: dict, current_user_id: str = Depends(auth_required)):
    """
    Create a new scheduled post for the authenticated user.
    
    Args:
        post_data: Post data including content, scheduled_time, campaign_id, etc.
        current_user_id: The authenticated user ID from Firebase token
        
    Returns:
        Created post details
    """
    try:
        # Verify the campaign exists and belongs to the user
        campaign = await campaign_schedules_collection.find_one({
            "_id": ObjectId(post_data["campaign_id"]),
            "user_id": current_user_id
        })
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found or you don't have permission to add posts to it"
            )
        
        # Prepare post data
        new_post = {
            "content": post_data["content"],
            "media_urls": post_data.get("media_urls", []),
            "scheduled_time": datetime.fromisoformat(post_data["scheduled_time"]),
            "campaign_id": ObjectId(post_data["campaign_id"]),
            "user_id": current_user_id,
            "status": "scheduled",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "platform": post_data.get("platform", "all"),
            "hashtags": post_data.get("hashtags", []),
            "mentions": post_data.get("mentions", [])
        }
        
        # Insert the post
        result = await scheduled_posts_collection.insert_one(new_post)
        
        # Return the created post
        created_post = await scheduled_posts_collection.find_one({"_id": result.inserted_id})
        created_post["id"] = str(created_post["_id"])
        created_post["campaign_id"] = str(created_post["campaign_id"])
        del created_post["_id"]
        
        return created_post
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error creating post: {e}")
        traceback_str = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the post: {str(e)}"
        )


@router.put("/scheduled-posts/{post_id}")
async def update_post(post_id: str, post_data: dict, current_user_id: str = Depends(auth_required)):
    """
    Update a scheduled post, ensuring it belongs to the authenticated user.
    
    Args:
        post_id: The ID of the post to update
        post_data: Updated post data
        current_user_id: The authenticated user ID from Firebase token
        
    Returns:
        Updated post details
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
            "content": post_data.get("content", existing_post["content"]),
            "media_urls": post_data.get("media_urls", existing_post.get("media_urls", [])),
            "scheduled_time": datetime.fromisoformat(post_data["scheduled_time"]) if "scheduled_time" in post_data else existing_post["scheduled_time"],
            "status": post_data.get("status", existing_post["status"]),
            "updated_at": datetime.utcnow(),
            "platform": post_data.get("platform", existing_post.get("platform", "all")),
            "hashtags": post_data.get("hashtags", existing_post.get("hashtags", [])),
            "mentions": post_data.get("mentions", existing_post.get("mentions", []))
        }
        
        # Update the post
        await scheduled_posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": update_data}
        )
        
        # Return the updated post
        updated_post = await scheduled_posts_collection.find_one({"_id": ObjectId(post_id)})
        updated_post["id"] = str(updated_post["_id"])
        updated_post["campaign_id"] = str(updated_post["campaign_id"])
        del updated_post["_id"]
        
        return updated_post
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error updating post: {e}")
        traceback_str = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the post: {str(e)}"
        )


@router.delete("/scheduled-posts/{post_id}")
async def delete_post(post_id: str, current_user_id: str = Depends(auth_required)):
    """
    Delete a scheduled post, ensuring it belongs to the authenticated user.
    
    Args:
        post_id: The ID of the post to delete
        current_user_id: The authenticated user ID from Firebase token
        
    Returns:
        Success message
    """
    try:
        print(f"Attempting to delete post with ID: {post_id}")
        
        # Try to convert to ObjectId, but handle the case where it might not be a valid ObjectId
        try:
            obj_id = ObjectId(post_id)
            # Find the post and ensure it belongs to the current user
            existing_post = await scheduled_posts_collection.find_one({
                "_id": obj_id,
                "user_id": current_user_id
            })
        except Exception as e:
            print(f"Error converting to ObjectId: {e}, trying with string ID")
            # If ObjectId conversion fails, try with the string ID directly
            existing_post = await scheduled_posts_collection.find_one({
                "id": post_id,  # Some posts might use 'id' instead of '_id'
                "user_id": current_user_id
            })
        
        if not existing_post:
            print(f"Post not found with ID: {post_id} for user: {current_user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or you don't have permission to delete it"
            )
        
        print(f"Found post to delete: {existing_post.get('_id')}")
        
        # Delete the post using the _id from the found document
        result = await scheduled_posts_collection.delete_one({"_id": existing_post.get("_id")})
        
        if result.deleted_count == 0:
            print(f"Failed to delete post with ID: {post_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete the post"
            )
        
        print(f"Successfully deleted post with ID: {post_id}")
        return {"message": "Post deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error deleting post: {e}")
        traceback_str = traceback.format_exc()
        print(traceback_str)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the post: {str(e)}"
        )