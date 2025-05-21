# # # # # from fastapi import FastAPI
# # # # # from fastapi.middleware.cors import CORSMiddleware
# # # # # from app.api.routes import (
# # # # #     chatbot,
# # # # #     image_gen,
# # # # #     caption_gen,
# # # # #     drafts,
# # # # #     post_now,
# # # # #     campaign_planner,
# # # # #     campaign_schedules  # Add this import
# # # # # )
# # # # # from pydantic import BaseModel
# # # # # from datetime import datetime
# # # # # from app.database import db
# # # # #
# # # # # app = FastAPI(title="SocialSync AI Services")
# # # # #
# # # # # # ✅ Allow CORS (Cross-Origin Requests)
# # # # # app.add_middleware(
# # # # #     CORSMiddleware,
# # # # #     allow_origins=["http://localhost:5173"],  # ✅ Set frontend URL
# # # # #     allow_credentials=True,
# # # # #     allow_methods=["*"],
# # # # #     allow_headers=["*"],
# # # # # )
# # # # #
# # # # # # Include routes
# # # # # app.include_router(chatbot.router, prefix="/api")
# # # # # app.include_router(image_gen.router, prefix="/api")
# # # # # app.include_router(caption_gen.router, prefix="/api")
# # # # # app.include_router(drafts.router, prefix="/api")  # ✅ Add Drafts Route
# # # # # app.include_router(campaign_planner.router, prefix="/api")
# # # # # app.include_router(post_now.router, prefix="/api")
# # # # # # app.include_router(campaign_schedules.router, prefix="/api")  # Add this line
# # # # # app.include_router(
# # # # #     campaign_schedules.router,
# # # # #     prefix="/api",
# # # # #     tags=["Campaign Schedules"]
# # # # # )
# # # # # @app.get("/")
# # # # # def home():
# # # # #     return {"message": "Welcome to SocialSync AI Services!"}
# # # # #
# # # # # @app.get("/status")
# # # # # async def status():
# # # # #     """Service health check"""
# # # # #     return {
# # # # #         "status": "operational",
# # # # #         "services": {
# # # # #             "gemini": bool(os.getenv("GEMINI_API_KEY")),
# # # # #             "groq": bool(os.getenv("GROQ_API_KEY")),
# # # # #             "huggingface": bool(os.getenv("HF_IMAGE_API_KEY")),
# # # # #             "advanced_huggingface": bool(os.getenv("HUGGINGFACE_API_KEY"))
# # # # #         }
# # # # #     }
# # # # #
# # # # # # Pydantic model for the request body
# # # # # class SchedulePostRequest(BaseModel):
# # # # #     caption: str
# # # # #     image_url: str
# # # # #     platform: str
# # # # #     scheduled_time: datetime
# # # # #
# # # # #
# # # # # @app.post("/api/schedule-post/")
# # # # # async def schedule_post(request: SchedulePostRequest):
# # # # #     # Here you can process the request data
# # # # #     # For example, save it in a database or schedule the task
# # # # #     print(f"Scheduling post: {request.caption} on {request.platform} at {request.scheduled_time}")
# # # # #
# # # # #     # Simulate success response
# # # # #     return {"message": "Post scheduled successfully"}
# # # # #
# # # # #
# # # # # @app.get("/api/scheduled-posts/")
# # # # # async def get_scheduled_posts():
# # # # #     # Assuming `db["scheduled_posts"]` is the collection where scheduled posts are stored
# # # # #     scheduled_posts = db["scheduled_posts"].find()  # Fetch all scheduled posts
# # # # #
# # # # #     # Convert the MongoDB cursor to a list or serialize it if needed
# # # # #     posts_list = list(scheduled_posts)  # Convert cursor to a list
# # # # #     return posts_list
# # # #
# # # #
# # # # from fastapi import FastAPI, HTTPException
# # # # from fastapi.middleware.cors import CORSMiddleware
# # # # from app.api.routes import (
# # # #     chatbot,
# # # #     image_gen,
# # # #     caption_gen,
# # # #     drafts,
# # # #     post_now,
# # # #     campaign_planner,
# # # #     campaign_schedules
# # # # )
# # # # from pydantic import BaseModel
# # # # from datetime import datetime
# # # # from app.database import db
# # # # from bson import ObjectId
# # # # import os
# # # #
# # # # app = FastAPI(title="SocialSync AI Services")
# # # #
# # # # # CORS Middleware
# # # # app.add_middleware(
# # # #     CORSMiddleware,
# # # #     allow_origins=["http://localhost:5173"],
# # # #     allow_credentials=True,
# # # #     allow_methods=["*"],
# # # #     allow_headers=["*"],
# # # # )
# # # #
# # # # # Include routes
# # # # app.include_router(chatbot.router, prefix="/api")
# # # # app.include_router(image_gen.router, prefix="/api")
# # # # app.include_router(caption_gen.router, prefix="/api")
# # # # app.include_router(drafts.router, prefix="/api")
# # # # app.include_router(campaign_planner.router, prefix="/api")
# # # # app.include_router(post_now.router, prefix="/api")
# # # # app.include_router(campaign_schedules.router, prefix="/api", tags=["Campaign Schedules"])
# # # #
# # # # @app.get("/")
# # # # def home():
# # # #     return {"message": "Welcome to SocialSync AI Services!"}
# # # #
# # # # @app.get("/status")
# # # # async def status():
# # # #     return {
# # # #         "status": "operational",
# # # #         "services": {
# # # #             "gemini": bool(os.getenv("GEMINI_API_KEY")),
# # # #             "groq": bool(os.getenv("GROQ_API_KEY")),
# # # #             "huggingface": bool(os.getenv("HF_IMAGE_API_KEY")),
# # # #             "advanced_huggingface": bool(os.getenv("HUGGINGFACE_API_KEY"))
# # # #         }
# # # #     }
# # # #
# # # # # Pydantic model for the request body
# # # # class SchedulePostRequest(BaseModel):
# # # #     caption: str
# # # #     image_url: str
# # # #     platform: str
# # # #     scheduled_time: datetime
# # # #
# # # # @app.post("/api/schedule-post/")
# # # # async def schedule_post(request: SchedulePostRequest):
# # # #     try:
# # # #         post_data = {
# # # #             "caption": request.caption,
# # # #             "image_url": request.image_url,
# # # #             "platform": request.platform,
# # # #             "scheduled_time": request.scheduled_time,
# # # #             "status": "scheduled",
# # # #             "created_at": datetime.utcnow()
# # # #         }
# # # #         result = db["scheduled_posts"].insert_one(post_data)
# # # #         return {
# # # #             "message": "Post scheduled successfully",
# # # #             "id": str(result.inserted_id)
# # # #         }
# # # #     except Exception as e:
# # # #         raise HTTPException(status_code=500, detail=f"Failed to schedule post: {str(e)}")
# # # #
# # # # @app.get("/api/scheduled-posts/")
# # # # async def get_scheduled_posts():
# # # #     try:
# # # #         scheduled_posts = db["scheduled_posts"].find()
# # # #         posts_list = [
# # # #             {
# # # #                 "id": str(post["_id"]),
# # # #                 "caption": post["caption"],
# # # #                 "image_url": post["image_url"],
# # # #                 "platform": post["platform"],
# # # #                 "scheduled_time": post["scheduled_time"],
# # # #                 "status": post["status"],
# # # #                 "created_at": post["created_at"]
# # # #             }
# # # #             for post in scheduled_posts
# # # #         ]
# # # #         return posts_list
# # # #     except Exception as e:
# # # #         raise HTTPException(status_code=500, detail=f"Failed to fetch scheduled posts: {str(e)}")
# # # #
# # # # @app.delete("/api/scheduled-posts/{post_id}")
# # # # async def delete_scheduled_post(post_id: str):
# # # #     try:
# # # #         result = db["scheduled_posts"].delete_one({"_id": ObjectId(post_id)})
# # # #         if result.deleted_count == 0:
# # # #             raise HTTPException(status_code=404, detail="Post not found")
# # # #         return {"message": "Post deleted successfully"}
# # # #     except Exception as e:
# # # #         raise HTTPException(status_code=500, detail=f"Failed to delete post: {str(e)}")
# # #
# # #
# # # from fastapi import FastAPI, HTTPException
# # # from fastapi.middleware.cors import CORSMiddleware
# # # from app.api.routes import (
# # #     chatbot,
# # #     image_gen,
# # #     caption_gen,
# # #     drafts,
# # #     post_now,
# # #     campaign_planner,
# # #     campaign_schedules
# # # )
# # # from pydantic import BaseModel
# # # from datetime import datetime
# # # from app.database import db
# # # from bson import ObjectId
# # # from typing import Union, List
# # # import os
# # #
# # # app = FastAPI(title="SocialSync AI Services")
# # #
# # # # CORS Middleware
# # # app.add_middleware(
# # #     CORSMiddleware,
# # #     allow_origins=["http://localhost:5173"],
# # #     allow_credentials=True,
# # #     allow_methods=["*"],
# # #     allow_headers=["*"],
# # # )
# # #
# # # # Include routes
# # # app.include_router(chatbot.router, prefix="/api")
# # # app.include_router(image_gen.router, prefix="/api")
# # # app.include_router(caption_gen.router, prefix="/api")
# # # app.include_router(drafts.router, prefix="/api")
# # # app.include_router(campaign_planner.router, prefix="/api")
# # # app.include_router(post_now.router, prefix="/api")
# # # app.include_router(campaign_schedules.router, prefix="/api", tags=["Campaign Schedules"])
# # #
# # # @app.get("/")
# # # def home():
# # #     return {"message": "Welcome to SocialSync AI Services!"}
# # #
# # # @app.get("/status")
# # # async def status():
# # #     return {
# # #         "status": "operational",
# # #         "services": {
# # #             "gemini": bool(os.getenv("GEMINI_API_KEY")),
# # #             "groq": bool(os.getenv("GROQ_API_KEY")),
# # #             "huggingface": bool(os.getenv("HF_IMAGE_API_KEY")),
# # #             "advanced_huggingface": bool(os.getenv("HUGGINGFACE_API_KEY"))
# # #         }
# # #     }
# # #
# # # # Pydantic model for the request body
# # # class SchedulePostRequest(BaseModel):
# # #     caption: str
# # #     image_url: Union[str, List[str]]  # Accept either a string or list of strings
# # #     platform: str
# # #     scheduled_time: datetime
# # #     is_carousel: bool = False
# # #
# # # @app.post("/api/schedule-post/")
# # # async def schedule_post(request: SchedulePostRequest):
# # #     try:
# # #         post_data = {
# # #             "caption": request.caption,
# # #             "image_url": request.image_url,  # Store as string or list
# # #             "platform": request.platform,
# # #             "scheduled_time": request.scheduled_time,
# # #             "status": "scheduled",
# # #             "created_at": datetime.utcnow(),
# # #             "is_carousel": request.is_carousel
# # #         }
# # #         result = db["scheduled_posts"].insert_one(post_data)
# # #         return {
# # #             "message": "Post scheduled successfully",
# # #             "id": str(result.inserted_id)
# # #         }
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=f"Failed to schedule post: {str(e)}")
# # #
# # # @app.get("/api/scheduled-posts/")
# # # async def get_scheduled_posts():
# # #     try:
# # #         scheduled_posts = db["scheduled_posts"].find()
# # #         posts_list = [
# # #             {
# # #                 "id": str(post["_id"]),
# # #                 "caption": post["caption"],
# # #                 "image_url": post["image_url"],  # Return as string or list
# # #                 "platform": post["platform"],
# # #                 "scheduled_time": post["scheduled_time"],
# # #                 "status": post["status"],
# # #                 "created_at": post["created_at"],
# # #                 "is_carousel": post.get("is_carousel", False)
# # #             }
# # #             for post in scheduled_posts
# # #         ]
# # #         return posts_list
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=f"Failed to fetch scheduled posts: {str(e)}")
# # #
# # # @app.delete("/api/scheduled-posts/{post_id}")
# # # async def delete_scheduled_post(post_id: str):
# # #     try:
# # #         result = db["scheduled_posts"].delete_one({"_id": ObjectId(post_id)})
# # #         if result.deleted_count == 0:
# # #             raise HTTPException(status_code=404, detail="Post not found")
# # #         return {"message": "Post deleted successfully"}
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=f"Failed to delete post: {str(e)}")
# #
# # #
# # # from fastapi import FastAPI, HTTPException
# # # from fastapi.middleware.cors import CORSMiddleware
# # # from app.api.routes import (
# # #     chatbot,
# # #     image_gen,
# # #     caption_gen,
# # #     drafts,
# # #     post_now,
# # #     campaign_planner,
# # #     campaign_schedules,
# # #     linkedin,
# # #     accounts
# # # )
# # # from pydantic import BaseModel
# # # from datetime import datetime
# # # from app.database import db
# # # from bson import ObjectId
# # # from typing import Union, List, Dict, Any
# # # from collections import defaultdict
# # # import os
# # #
# # # app = FastAPI(title="SocialSync AI Services")
# # #
# # # # CORS Middleware
# # # app.add_middleware(
# # #     CORSMiddleware,
# # #     allow_origins=["http://localhost:5173"],
# # #     allow_credentials=True,
# # #     allow_methods=["*"],
# # #     allow_headers=["*"],
# # # )
# # #
# # # # Include routes
# # # app.include_router(chatbot.router, prefix="/api")
# # # app.include_router(image_gen.router, prefix="/api")
# # # app.include_router(caption_gen.router, prefix="/api")
# # # app.include_router(drafts.router, prefix="/api")
# # # app.include_router(campaign_planner.router, prefix="/api")
# # # app.include_router(post_now.router, prefix="/api")
# # # app.include_router(campaign_schedules.router, prefix="/api", tags=["Campaign Schedules"])
# # # app.include_router(linkedin.router, prefix="/api/linkedin", tags=["linkedin"])
# # # app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
# # # @app.get("/")
# # # def home():
# # #     return {"message": "Welcome to SocialSync AI Services!"}
# # #
# # # @app.get("/status")
# # # async def status():
# # #     return {
# # #         "status": "operational",
# # #         "services": {
# # #             "gemini": bool(os.getenv("GEMINI_API_KEY")),
# # #             "groq": bool(os.getenv("GROQ_API_KEY")),
# # #             "huggingface": bool(os.getenv("HF_IMAGE_API_KEY")),
# # #             "advanced_huggingface": bool(os.getenv("HUGGINGFACE_API_KEY"))
# # #         }
# # #     }
# # #
# # # # Pydantic model for the request body
# # # class SchedulePostRequest(BaseModel):
# # #     caption: str
# # #     image_url: Union[str, List[str]]  # Accept either a string or list of strings
# # #     platform: str
# # #     scheduled_time: datetime
# # #     is_carousel: bool = False
# # #
# # # @app.post("/api/schedule-post/")
# # # async def schedule_post(request: SchedulePostRequest):
# # #     try:
# # #         post_data = {
# # #             "caption": request.caption,
# # #             "image_url": request.image_url,  # Store as string or list
# # #             "platform": request.platform,
# # #             "scheduled_time": request.scheduled_time,
# # #             "status": "scheduled",
# # #             "created_at": datetime.utcnow(),
# # #             "is_carousel": request.is_carousel
# # #         }
# # #         result = db["scheduled_posts"].insert_one(post_data)
# # #         return {
# # #             "message": "Post scheduled successfully",
# # #             "id": str(result.inserted_id)
# # #         }
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=f"Failed to schedule post: {str(e)}")
# # #
# # # @app.get("/api/scheduled-posts/")
# # # async def get_scheduled_posts():
# # #     try:
# # #         scheduled_posts = db["scheduled_posts"].find()
# # #         posts_list = [
# # #             {
# # #                 "id": str(post["_id"]),
# # #                 "caption": post["caption"],
# # #                 "image_url": post["image_url"],  # Return as string or list
# # #                 "platform": post["platform"],
# # #                 "scheduled_time": post["scheduled_time"],
# # #                 "status": post["status"],
# # #                 "created_at": post["created_at"],
# # #                 "is_carousel": post.get("is_carousel", False)
# # #             }
# # #             for post in scheduled_posts
# # #         ]
# # #         return posts_list
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=f"Failed to fetch scheduled posts: {str(e)}")
# # #
# # # @app.delete("/api/scheduled-posts/{post_id}")
# # # async def delete_scheduled_post(post_id: str):
# # #     try:
# # #         result = db["scheduled_posts"].delete_one({"_id": ObjectId(post_id)})
# # #         if result.deleted_count == 0:
# # #             raise HTTPException(status_code=404, detail="Post not found")
# # #         return {"message": "Post deleted successfully"}
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=f"Failed to delete post: {str(e)}")
# # #
# # #
# # # @app.get("/api/scheduled-posts/stats")
# # # async def get_scheduled_posts_stats():
# # #     try:
# # #         # Get all scheduled posts
# # #         scheduled_posts = db["scheduled_posts"].find()
# # #
# # #         # Initialize stats
# # #         stats = {
# # #             "total_posts": 0,
# # #             "by_platform": defaultdict(int),
# # #             "by_status": defaultdict(int)
# # #         }
# # #
# # #         # Calculate stats
# # #         for post in scheduled_posts:
# # #             stats["total_posts"] += 1
# # #             stats["by_platform"][post["platform"]] += 1
# # #             stats["by_status"][post["status"]] += 1
# # #
# # #         # Convert defaultdict to regular dict for JSON serialization
# # #         stats["by_platform"] = dict(stats["by_platform"])
# # #         stats["by_status"] = dict(stats["by_status"])
# # #
# # #         return stats
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")
# # #
# # #
# # # @app.get("/api/team-members")
# # # async def get_team_members():
# # #     try:
# # #         # In a real app, you would fetch from your database
# # #         # For now, returning mock data
# # #         return [
# # #             {"id": "1", "username": "user1", "name": "John Doe"},
# # #             {"id": "2", "username": "user2", "name": "Jane Smith"},
# # #             {"id": "3", "username": "user3", "name": "Bob Johnson"}
# # #         ]
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=f"Failed to fetch team members: {str(e)}")
# # #
# # #
# # # @app.patch("/api/scheduled-posts/{post_id}")
# # # async def update_scheduled_post(post_id: str, update_data: Dict[str, Any]):
# # #     try:
# # #         # Remove None values from update data
# # #         update_data = {k: v for k, v in update_data.items() if v is not None}
# # #
# # #         if not update_data:
# # #             raise HTTPException(status_code=400, detail="No data provided for update")
# # #
# # #         result = db["scheduled_posts"].update_one(
# # #             {"_id": ObjectId(post_id)},
# # #             {"$set": update_data}
# # #         )
# # #
# # #         if result.matched_count == 0:
# # #             raise HTTPException(status_code=404, detail="Post not found")
# # #
# # #         return {"message": "Post updated successfully"}
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=f"Failed to update post: {str(e)}")
# # #
# # #     class PostRequest(BaseModel):
# # #         image_url: str | list[str]
# # #         caption: str
# # #         access_token: str
# # #         platform: str
# # #         is_carousel: bool
# # #
# # #     @router.post("/post-now/")
# # #     async def post_now(request: PostRequest):
# # #         try:
# # #             # Logic to post to the platform (e.g., Facebook)
# # #             return {"id": "post_id_123"}
# # #         except Exception as e:
# # #             raise HTTPException(status_code=400, detail=str(e))
# #
# # from fastapi import FastAPI, HTTPException
# # from fastapi.middleware.cors import CORSMiddleware
# # from app.api.routes import (
# #     chatbot,
# #     image_gen,
# #     caption_gen,
# #     drafts,
# #     post_now,
# #     campaign_planner,
# #     campaign_schedules,
# #     linkedin,
# #     accounts,
# #     auth
# # )
# # from pydantic import BaseModel
# # from datetime import datetime
# # from app.database import db
# # from bson import ObjectId
# # from typing import Union, List, Dict, Any
# # from collections import defaultdict
# # import os
# # from app.database import create_indexes
# #
# #
# # app = FastAPI(title="SocialSync AI Services")
# #
# # # CORS Middleware
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["http://localhost:5173"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )
# #
# # # Include routes
# # app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# # app.include_router(chatbot.router, prefix="/api")
# # app.include_router(image_gen.router, prefix="/api")
# # app.include_router(caption_gen.router, prefix="/api")
# # app.include_router(drafts.router, prefix="/api")
# # app.include_router(campaign_planner.router, prefix="/api")
# # app.include_router(post_now.router, prefix="/api")
# # app.include_router(campaign_schedules.router, prefix="/api", tags=["Campaign Schedules"])
# # app.include_router(linkedin.router, prefix="/api/linkedin", tags=["linkedin"])
# # app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
# #
# # @app.get("/")
# # def home():
# #     return {"message": "Welcome to SocialSync AI Services!"}
# #
# # @app.on_event("startup")
# # async def startup_db_client():
# #     await create_indexes()
# # @app.get("/status")
# # async def status():
# #     return {
# #         "status": "operational",
# #         "services": {
# #             "gemini": bool(os.getenv("GEMINI_API_KEY")),
# #             "groq": bool(os.getenv("GROQ_API_KEY")),
# #             "huggingface": bool(os.getenv("HF_IMAGE_API_KEY")),
# #             "advanced_huggingface": bool(os.getenv("HUGGINGFACE_API_KEY")),
# #             "linkedin": bool(os.getenv("LINKEDIN_CLIENT_ID") and os.getenv("LINKEDIN_CLIENT_SECRET"))
# #         }
# #     }
# #
# # # Pydantic model for the request body
# # class SchedulePostRequest(BaseModel):
# #     caption: str
# #     image_url: Union[str, List[str]]  # Accept either a string or list of strings
# #     platform: str
# #     scheduled_time: datetime
# #     is_carousel: bool = False
# #
# #
# # @app.post("/api/schedule-post/")
# # async def schedule_post(request: SchedulePostRequest):
# #     try:
# #         post_data = {
# #             "caption": request.caption,
# #             "image_url": request.image_url,
# #             "platform": request.platform,
# #             "scheduled_time": request.scheduled_time,
# #             "status": "scheduled",
# #             "created_at": datetime.utcnow(),
# #             "is_carousel": request.is_carousel
# #         }
# #         # Add await here
# #         result = await db["scheduled_posts"].insert_one(post_data)
# #         return {
# #             "message": "Post scheduled successfully",
# #             "id": str(result.inserted_id)
# #         }
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Failed to schedule post: {str(e)}")
# #
# #
# # @app.get("/api/scheduled-posts/")
# # async def get_scheduled_posts():
# #     try:
# #         # Get cursor and convert to list
# #         cursor = db["scheduled_posts"].find()
# #         scheduled_posts = await cursor.to_list(length=None)
# #
# #         posts_list = [
# #             {
# #                 "id": str(post["_id"]),
# #                 "caption": post["caption"],
# #                 "image_url": post["image_url"],
# #                 "platform": post["platform"],
# #                 "scheduled_time": post["scheduled_time"],
# #                 "status": post["status"],
# #                 "created_at": post["created_at"],
# #                 "is_carousel": post.get("is_carousel", False)
# #             }
# #             for post in scheduled_posts
# #         ]
# #         return posts_list
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Failed to fetch scheduled posts: {str(e)}")
# #
# #
# # @app.delete("/api/scheduled-posts/{post_id}")
# # async def delete_scheduled_post(post_id: str):
# #     try:
# #         # Add await here
# #         result = await db["scheduled_posts"].delete_one({"_id": ObjectId(post_id)})
# #         if result.deleted_count == 0:
# #             raise HTTPException(status_code=404, detail="Post not found")
# #         return {"message": "Post deleted successfully"}
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Failed to delete post: {str(e)}")
# #
# #
# # @app.get("/api/scheduled-posts/stats")
# # async def get_scheduled_posts_stats():
# #     try:
# #         # Get cursor and convert to list
# #         cursor = db["scheduled_posts"].find()
# #         scheduled_posts = await cursor.to_list(length=None)
# #
# #         # The rest of the function can stay the same
# #         stats = {
# #             "total_posts": 0,
# #             "by_platform": defaultdict(int),
# #             "by_status": defaultdict(int)
# #         }
# #
# #         for post in scheduled_posts:
# #             stats["total_posts"] += 1
# #             stats["by_platform"][post["platform"]] += 1
# #             stats["by_status"][post["status"]] += 1
# #
# #         stats["by_platform"] = dict(stats["by_platform"])
# #         stats["by_status"] = dict(stats["by_status"])
# #
# #         return stats
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")
# #
# #
# # @app.patch("/api/scheduled-posts/{post_id}")
# # async def update_scheduled_post(post_id: str, update_data: Dict[str, Any]):
# #     try:
# #         # Remove None values from update data
# #         update_data = {k: v for k, v in update_data.items() if v is not None}
# #
# #         if not update_data:
# #             raise HTTPException(status_code=400, detail="No data provided for update")
# #
# #         # Add await here
# #         result = await db["scheduled_posts"].update_one(
# #             {"_id": ObjectId(post_id)},
# #             {"$set": update_data}
# #         )
# #
# #         if result.matched_count == 0:
# #             raise HTTPException(status_code=404, detail="Post not found")
# #
# #         return {"message": "Post updated successfully"}
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Failed to update post: {str(e)}")
# #
# # @app.get("/api/team-members")
# # async def get_team_members():
# #     try:
# #         # In a real app, you would fetch from your database
# #         # For now, returning mock data
# #         return [
# #             {"id": "1", "username": "user1", "name": "John Doe"},
# #             {"id": "2", "username": "user2", "name": "Jane Smith"},
# #             {"id": "3", "username": "user3", "name": "Bob Johnson"}
# #         ]
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Failed to fetch team members: {str(e)}")
# #
#
#
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from app.api.routes import (
#     chatbot,
#     image_gen,
#     caption_gen,
#     drafts,
#     post_now,
#     campaign_planner,
#     campaign_schedules,
#     linkedin,
#     accounts,
#     auth,
#     scheduled_posts  # Import our new router
# )
# from app.database import create_indexes
# from app.services.scheduler import start_scheduler, stop_scheduler  # Import our scheduler functions
#
# app = FastAPI(title="SocialSync AI Services")
#
# # CORS Middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Include routes
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(chatbot.router, prefix="/api")
# app.include_router(image_gen.router, prefix="/api")
# app.include_router(caption_gen.router, prefix="/api")
# app.include_router(drafts.router, prefix="/api")
# app.include_router(campaign_planner.router, prefix="/api")
# app.include_router(post_now.router, prefix="/api")
# app.include_router(campaign_schedules.router, prefix="/api", tags=["Campaign Schedules"])
# app.include_router(linkedin.router, prefix="/api/linkedin", tags=["linkedin"])
# app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
# app.include_router(scheduled_posts.router, prefix="/api", tags=["Scheduled Posts"])  # Add our new router
#
#
# @app.get("/")
# def home():
#     return {"message": "Welcome to SocialSync AI Services!"}
#
#
# @app.on_event("startup")
# async def startup_db_client():
#     await create_indexes()
#     await start_scheduler()  # Start the scheduler at application startup
#
#
# @app.on_event("shutdown")
# async def shutdown_scheduler():
#     await stop_scheduler()  # Stop the scheduler at application shutdown
#
#
# @app.get("/status")
# async def status():
#     return {
#         "status": "operational",
#         "services": {
#             "scheduler": "active",
#             "gemini": True,
#             "groq": True,
#             "huggingface": True,
#             "advanced_huggingface": True,
#             "linkedin": True
#         }
#     }
#
#
# # Include the existing routes for scheduled posts
# # These can be phased out or redirected to our new endpoints
# from datetime import datetime
# from bson import ObjectId
# from typing import List, Dict, Any
#
# # Assuming you have db imported from app.database
# from app.database import db
#
#
# @app.post("/api/schedule-post/")
# async def legacy_schedule_post(request: Dict[str, Any]):
#     try:
#         post_data = {
#             "caption": request.get("caption"),
#             "image_url": request.get("image_url"),
#             "platform": request.get("platform"),
#             "scheduled_time": request.get("scheduled_time"),
#             "status": "scheduled",
#             "created_at": datetime.utcnow(),
#             "is_carousel": request.get("is_carousel", False)
#         }
#
#         # Add await here
#         result = await db["scheduled_posts"].insert_one(post_data)
#         return {
#             "message": "Post scheduled successfully",
#             "id": str(result.inserted_id)
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to schedule post: {str(e)}")
#
#
# @app.get("/api/scheduled-posts/")
# async def legacy_get_scheduled_posts():
#     try:
#         # Get cursor and convert to list
#         cursor = db["scheduled_posts"].find()
#         scheduled_posts = await cursor.to_list(length=None)
#
#         posts_list = [
#             {
#                 "id": str(post["_id"]),
#                 "caption": post["caption"],
#                 "image_url": post["image_url"],
#                 "platform": post["platform"],
#                 "scheduled_time": post["scheduled_time"],
#                 "status": post["status"],
#                 "created_at": post["created_at"],
#                 "is_carousel": post.get("is_carousel", False)
#             }
#             for post in scheduled_posts
#         ]
#         return posts_list
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch scheduled posts: {str(e)}")
#
#
# @app.delete("/api/scheduled-posts/{post_id}")
# async def legacy_delete_scheduled_post(post_id: str):
#     try:
#         # Add await here
#         result = await db["scheduled_posts"].delete_one({"_id": ObjectId(post_id)})
#         if result.deleted_count == 0:
#             raise HTTPException(status_code=404, detail="Post not found")
#         return {"message": "Post deleted successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to delete post: {str(e)}")
#
#
# @app.get("/api/scheduled-posts/stats")
# async def legacy_get_scheduled_posts_stats():
#     try:
#         # Get cursor and convert to list
#         cursor = db["scheduled_posts"].find()
#         scheduled_posts = await cursor.to_list(length=None)
#
#         # The rest of the function can stay the same
#         stats = {
#             "total_posts": 0,
#             "by_platform": {},
#             "by_status": {}
#         }
#
#         for post in scheduled_posts:
#             stats["total_posts"] += 1
#
#             # Track by platform
#             platform = post.get("platform", "unknown")
#             if platform in stats["by_platform"]:
#                 stats["by_platform"][platform] += 1
#             else:
#                 stats["by_platform"][platform] = 1
#
#             # Track by status
#             status = post.get("status", "unknown")
#             if status in stats["by_status"]:
#                 stats["by_status"][status] += 1
#             else:
#                 stats["by_status"][status] = 1
#
#         return stats
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")
#
#
# @app.patch("/api/scheduled-posts/{post_id}")
# async def legacy_update_scheduled_post(post_id: str, update_data: Dict[str, Any]):
#     try:
#         # Remove None values from update data
#         update_data = {k: v for k, v in update_data.items() if v is not None}
#
#         if not update_data:
#             raise HTTPException(status_code=400, detail="No data provided for update")
#
#         # Add await here
#         result = await db["scheduled_posts"].update_one(
#             {"_id": ObjectId(post_id)},
#             {"$set": update_data}
#         )
#
#         if result.matched_count == 0:
#             raise HTTPException(status_code=404, detail="Post not found")
#
#         return {"message": "Post updated successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to update post: {str(e)}")
#
#
# @app.get("/api/team-members")
# async def get_team_members():
#     try:
#         # In a real app, you would fetch from your database
#         # For now, returning mock data
#         return [
#             {"id": "1", "username": "user1", "name": "John Doe"},
#             {"id": "2", "username": "user2", "name": "Jane Smith"},
#             {"id": "3", "username": "user3", "name": "Bob Johnson"}
#         ]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch team members: {str(e)}")

from fastapi import FastAPI, HTTPException
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
    scheduled_posts  # Import our new router
)
from app.database import create_indexes
from app.services.scheduler import start_scheduler, stop_scheduler  # Import our scheduler functions

app = FastAPI(title="SocialSync AI Services")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chatbot.router, prefix="/api")
app.include_router(image_gen.router, prefix="/api")
app.include_router(caption_gen.router, prefix="/api")
app.include_router(drafts.router, prefix="/api")
app.include_router(campaign_planner.router, prefix="/api")
app.include_router(post_now.router, prefix="/api")
app.include_router(campaign_schedules.router, prefix="/api", tags=["Campaign Schedules"])
app.include_router(linkedin.router, prefix="/api/linkedin", tags=["linkedin"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(scheduled_posts.router, prefix="/api", tags=["Scheduled Posts"])  # Add our new router


@app.get("/")
def home():
    return {"message": "Welcome to SocialSync AI Services!"}


@app.on_event("startup")
async def startup_db_client():
    await create_indexes()
    await start_scheduler()  # Start the scheduler at application startup


@app.on_event("shutdown")
async def shutdown_scheduler():
    await stop_scheduler()  # Stop the scheduler at application shutdown


@app.get("/status")
async def status():
    return {
        "status": "operational",
        "services": {
            "scheduler": "active",
            "gemini": True,
            "groq": True,
            "huggingface": True,
            "advanced_huggingface": True,
            "linkedin": True
        }
    }


# Add a specific route for stats to avoid the ObjectId confusion
@app.get("/api/scheduled-posts/stats")
async def stats_endpoint():
    """Special endpoint to forward to the correct stats handler"""
    # This is just a redirect to our new endpoint
    return await scheduled_posts.get_scheduled_posts_stats()


# Include the existing routes for scheduled posts
# These can be phased out or redirected to our new endpoints
from datetime import datetime
from bson import ObjectId
from typing import List, Dict, Any

# Assuming you have db imported from app.database
from app.database import db


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
            "is_carousel": request.get("is_carousel", False)
        }

        # Add await here
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
        # Get cursor and convert to list
        cursor = db["scheduled_posts"].find()
        scheduled_posts = await cursor.to_list(length=None)

        posts_list = [
            {
                "id": str(post["_id"]),
                "caption": post["caption"],
                "image_url": post["image_url"],
                "platform": post["platform"],
                "scheduled_time": post["scheduled_time"],
                "status": post["status"],
                "created_at": post["created_at"],
                "is_carousel": post.get("is_carousel", False)
            }
            for post in scheduled_posts
        ]
        return posts_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch scheduled posts: {str(e)}")


@app.delete("/api/scheduled-posts/{post_id}")
async def legacy_delete_scheduled_post(post_id: str):
    try:
        # Add await here
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

        # Add await here
        result = await db["scheduled_posts"].update_one(
            {"_id": ObjectId(post_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Post not found")

        return {"message": "Post updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update post: {str(e)}")


@app.get("/api/team-members")
async def get_team_members():
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