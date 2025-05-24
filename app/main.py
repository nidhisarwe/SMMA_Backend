# Backend/app/main.py - UPDATED TO INCLUDE MISSING ENDPOINTS
# IMPORTANT: Load environment variables FIRST before any other imports
import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    
    # Get the path to the .env file (should be in the project root)
    env_path = Path(__file__).parent.parent / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[SUCCESS] Loaded environment variables from: {env_path}")
    else:
        print(f"[WARNING] .env file not found at: {env_path}")
        # Try loading from current directory
        load_dotenv()
        print("[SUCCESS] Attempted to load .env from current directory")
        
    # Debug: Print key environment variables
    print("[INFO] Key Environment Variables:")
    print(f"  FIREBASE_PROJECT_ID: {os.getenv('FIREBASE_PROJECT_ID')}")
    print(f"  FIREBASE_SERVICE_ACCOUNT_PATH: {os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')}")
    print(f"  MONGO_URI: {'SET' if os.getenv('MONGO_URI') else 'NOT SET'}")
        
except ImportError:
    print("[ERROR] python-dotenv not installed. Install with: pip install python-dotenv")
    print("[WARNING] Environment variables will only be loaded from system environment")

# Now import FastAPI and other modules
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import (
    chatbot,
    image_gen,
    caption_gen,
    drafts,
    post_now,
    campaign_planner,
    campaign_schedules,
    linkedin,
    accounts,
    auth,
    scheduled_posts
)
# Import the missing endpoints
from app.api.routes.missing_endpoints import router as missing_endpoints_router
from app.database import create_indexes
from app.services.scheduler import start_scheduler, stop_scheduler
from typing import Optional
from datetime import datetime
from bson import ObjectId
from typing import List, Dict, Any
from app.database import db

app = FastAPI(title="SocialSync AI Services")

# Enhanced CORS Middleware with more permissive settings for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers
    max_age=86400  # Cache preflight requests for 24 hours
)

# Include routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chatbot.router, prefix="/api")
app.include_router(image_gen.router, prefix="/api")
app.include_router(caption_gen.router, prefix="/api")
app.include_router(drafts.router, prefix="/api")
app.include_router(campaign_planner.router, prefix="/api")
app.include_router(post_now.router, prefix="/api")
app.include_router(campaign_schedules.router, prefix="/api/campaign-schedules", tags=["Campaign Schedules"])
app.include_router(linkedin.router, prefix="/api/linkedin", tags=["LinkedIn"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(scheduled_posts.router, prefix="/api", tags=["Scheduled Posts"])

# FIXED: Add the missing endpoints router
app.include_router(missing_endpoints_router, prefix="/api", tags=["Missing Endpoints"])

@app.get("/")
def home():
    return {"message": "Welcome to SocialSync AI Services!"}

# Debug endpoint for authentication testing
@app.get("/api/debug/auth")
async def debug_auth(authorization: Optional[str] = Header(None)):
    """Debug endpoint to test authentication"""
    result = {
        "authorization_header": authorization,
        "firebase_project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "firebase_configured": bool(os.getenv("FIREBASE_PROJECT_ID")),
        "service_account_path": os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH"),
        "service_account_exists": os.path.exists(os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "")),
    }
    
    if authorization:
        try:
            # Try to extract and verify token
            token = authorization.replace("Bearer ", "")
            result["token_preview"] = token[:20] + "..." if len(token) > 20 else token
            
            # Try to verify
            from app.core.firebase_admin import verify_firebase_token
            uid = verify_firebase_token(token)
            result["verification_result"] = uid
            result["verification_success"] = uid is not None
            
        except Exception as e:
            result["verification_error"] = str(e)
            result["verification_success"] = False
    
    return result

# Missing endpoints for calendar and stats
@app.get("/api/scheduled-posts-stats/")
async def get_scheduled_posts_stats():
    """Get statistics for scheduled posts."""
    try:
        cursor = db["scheduled_posts"].find()
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
        
        return {
            "total_posts": total_posts,
            "by_platform": by_platform,
            "by_status": by_status
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )

@app.get("/api/scheduled-posts")
async def get_scheduled_posts():
    """Get all scheduled posts."""
    try:
        cursor = db["scheduled_posts"].find().sort("scheduled_time", 1)
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
        
        return {"posts": posts}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scheduled posts: {str(e)}"
        )

@app.get("/api/team-members")
async def get_team_members():
    """Get team members (mock data for now)."""
    try:
        # In a real app, you would fetch from your database
        # For now, returning mock data
        return [
            {"id": "1", "username": "user1", "name": "John Doe"},
            {"id": "2", "username": "user2", "name": "Jane Smith"},
            {"id": "3", "username": "user3", "name": "Bob Johnson"}
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch team members: {str(e)}")

@app.on_event("startup")
async def startup_db_client():
    await create_indexes()
    await start_scheduler()

@app.on_event("shutdown")
async def shutdown_scheduler():
    await stop_scheduler()

@app.get("/status")
async def status():
    return {
        "status": "operational",
        "environment": {
            "firebase_project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "firebase_configured": bool(os.getenv("FIREBASE_PROJECT_ID")),
            "mongo_configured": bool(os.getenv("MONGO_URI")),
        },
        "services": {
            "scheduler": "active",
            "gemini": True,
            "groq": True,
            "huggingface": True,
            "advanced_huggingface": True,
            "linkedin": True,
            "firebase": bool(os.getenv("FIREBASE_PROJECT_ID")),
        }
    }

# Legacy routes for backward compatibility
@app.post("/api/schedule-post/")
async def legacy_schedule_post(request: Dict[str, Any]):
    try:
        post_data = {
            "caption": request.get("caption"),
            "image_url": request.get("image_url"),
            "platform": request.get("platform"),
            "scheduled_time": request.get("scheduled_time"),
            "status": "scheduled",
            "created_at": datetime.utcnow(),
            "is_carousel": request.get("is_carousel", False),
            "user_id": request.get("user_id", "default_user")  # Add user_id for consistency
        }

        result = await db["scheduled_posts"].insert_one(post_data)
        return {
            "message": "Post scheduled successfully",
            "id": str(result.inserted_id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule post: {str(e)}")

@app.get("/api/scheduled-posts/")
async def legacy_get_scheduled_posts():
    try:
        cursor = db["scheduled_posts"].find()
        scheduled_posts = await cursor.to_list(length=None)

        posts_list = [
            {
                "id": str(post["_id"]),
                "caption": post.get("caption", ""),
                "content": post.get("content", post.get("caption", "")),  # Add content field
                "image_url": post.get("image_url"),
                "image_urls": post.get("image_urls", post.get("image_url")),  # Add image_urls
                "platform": post.get("platform"),
                "scheduled_time": post.get("scheduled_time"),
                "status": post.get("status", "scheduled"),
                "created_at": post.get("created_at"),
                "is_carousel": post.get("is_carousel", False),
                "user_id": post.get("user_id", "default_user"),
                "tags": post.get("tags", []),
                "assigned_to": post.get("assigned_to"),
                "theme": post.get("theme", ""),
                "title": post.get("title", ""),
                "call_to_action": post.get("call_to_action", "")
            }
            for post in scheduled_posts
        ]
        return posts_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch scheduled posts: {str(e)}")

@app.delete("/api/scheduled-posts/{post_id}")
async def legacy_delete_scheduled_post(post_id: str):
    try:
        result = await db["scheduled_posts"].delete_one({"_id": ObjectId(post_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Post not found")
        return {"message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete post: {str(e)}")

@app.patch("/api/scheduled-posts/{post_id}")
async def legacy_update_scheduled_post(post_id: str, update_data: Dict[str, Any]):
    try:
        # Remove None values from update data
        update_data = {k: v for k, v in update_data.items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="No data provided for update")

        # Add updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()

        result = await db["scheduled_posts"].update_one(
            {"_id": ObjectId(post_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Post not found")

        return {"message": "Post updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update post: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)