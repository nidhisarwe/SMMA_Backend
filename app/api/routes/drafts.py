# # # # from fastapi import APIRouter, HTTPException, Body
# # # # from app.database import drafts_collection  # ✅ Use the explicit collection
# # # # from app.models import Draft
# # # #
# # # # router = APIRouter()
# # # #
# # # # @router.post("/save-draft/")
# # # # async def save_draft(
# # # #     caption: str = Body(..., embed=True),
# # # #     platform: str = Body(..., embed=True),
# # # #     image_url: str = Body(None, embed=True),
# # # #     prompt: str = Body(None, embed=True)
# # # # ):
# # # #     try:
# # # #         draft = Draft(caption=caption, platform=platform, image_url=image_url, prompt=prompt)
# # # #
# # # #         # ✅ Ensure collection is properly used
# # # #         drafts_collection.insert_one(draft.to_dict())
# # # #
# # # #         return {"message": "Draft saved successfully!", "draft_id": str(draft._id)}
# # # #     except Exception as e:
# # # #         raise HTTPException(status_code=500, detail=str(e))
# # #
# # # #
# # # # from fastapi import APIRouter, HTTPException, Body
# # # # from app.database import drafts_collection
# # # # from app.models import Draft
# # # # from bson import ObjectId
# # # #
# # # # router = APIRouter()
# # # #
# # # # @router.post("/save-draft/")
# # # # async def save_draft(
# # # #     caption: str = Body(..., embed=True),
# # # #     platform: str = Body(..., embed=True),
# # # #     image_url: str = Body(None, embed=True),
# # # #     prompt: str = Body(None, embed=True)
# # # # ):
# # # #     try:
# # # #         draft = Draft(caption=caption, platform=platform, image_url=image_url, prompt=prompt)
# # # #         drafts_collection.insert_one(draft.to_dict())
# # # #         return {"message": "Draft saved successfully!", "draft_id": str(draft._id)}
# # # #     except Exception as e:
# # # #         raise HTTPException(status_code=500, detail=str(e))
# # # #
# # # # # ✅ New route to fetch all drafts
# # # # @router.get("/get-drafts/")
# # # # async def get_drafts():
# # # #     try:
# # # #         drafts = list(drafts_collection.find())
# # # #         for draft in drafts:
# # # #             draft["_id"] = str(draft["_id"])  # Convert ObjectId to str for JSON serialization
# # # #         return drafts
# # # #     except Exception as e:
# # # #         raise HTTPException(status_code=500, detail=str(e))
# # #
# # #
# # # from fastapi import APIRouter, HTTPException, status
# # # from pydantic import BaseModel, Field, validator
# # # from datetime import datetime
# # # from typing import List, Optional, Union
# # # from app.database import drafts_collection
# # # import logging
# # # import re
# # #
# # # router = APIRouter()
# # #
# # # logger = logging.getLogger(__name__)
# # #
# # #
# # # class DraftCreate(BaseModel):
# # #     caption: str = Field(..., min_length=1, max_length=2200)
# # #     platform: str = Field(..., pattern=r"^(instagram|facebook|twitter|linkedin)$")
# # #     image_url: Optional[Union[str, List[str]]] = None
# # #     prompt: Optional[str] = Field(None, max_length=500)
# # #     is_carousel: bool = False
# # #
# # #     @validator('image_url')
# # #     def validate_image_url(cls, v, values):
# # #         if values.get('is_carousel') and isinstance(v, str):
# # #             return [v]
# # #         return v
# # #
# # #
# # # @router.post("/save-draft/", status_code=status.HTTP_201_CREATED)
# # # async def save_draft(draft: DraftCreate):
# # #     try:
# # #         # Validate platform separately for better error messages
# # #         if not re.fullmatch(r"^(instagram|facebook|twitter|linkedin)$", draft.platform):
# # #             raise HTTPException(
# # #                 status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
# # #                 detail={
# # #                     "status": "error",
# # #                     "message": "Invalid platform",
# # #                     "errors": [{
# # #                         "loc": ["platform"],
# # #                         "msg": "Must be one of: instagram, facebook, twitter, linkedin"
# # #                     }]
# # #                 }
# # #             )
# # #
# # #         draft_data = draft.dict()
# # #         draft_data["created_at"] = datetime.now()
# # #
# # #         # Convert single image to array if carousel
# # #         if draft.is_carousel and isinstance(draft.image_url, str):
# # #             draft_data["image_url"] = [draft.image_url]
# # #
# # #         result = drafts_collection.insert_one(draft_data)
# # #
# # #         return {
# # #             "status": "success",
# # #             "message": "Draft saved successfully",
# # #             "draft_id": str(result.inserted_id)
# # #         }
# # #
# # #     except HTTPException:
# # #         raise
# # #     except Exception as e:
# # #         logger.error(f"Draft save error: {str(e)}")
# # #         raise HTTPException(
# # #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
# # #             detail={
# # #                 "status": "error",
# # #                 "message": "Failed to save draft",
# # #                 "error": str(e)
# # #             }
# # #         )
# # #
# # #
# # # @router.get("/get-drafts/")
# # # async def get_drafts():
# # #     try:
# # #         drafts = []
# # #         for draft in drafts_collection.find():
# # #             draft["_id"] = str(draft["_id"])  # Convert ObjectId to string
# # #             drafts.append(draft)
# # #         return drafts
# # #     except Exception as e:
# # #         return {"error": str(e)}
# #
# # from fastapi import APIRouter, HTTPException, status
# # from pydantic import BaseModel, Field, validator
# # from datetime import datetime
# # from typing import List, Optional, Union
# # from app.database import drafts_collection
# # import logging
# # import re
# # from fastapi import Query
# #
# # router = APIRouter()
# #
# # logger = logging.getLogger(__name__)
# #
# # class DraftCreate(BaseModel):
# #     caption: str = Field(..., min_length=1, max_length=2200)
# #     platform: str = Field(..., pattern=r"^(instagram|facebook|twitter|linkedin)$")
# #     image_url: Optional[Union[str, List[str]]] = None
# #     prompt: Optional[str] = Field(None, max_length=500)
# #     is_carousel: bool = False
# #
# #     @validator('image_url')
# #     def validate_image_url(cls, v, values):
# #         if values.get('is_carousel'):
# #             if not v:
# #                 raise ValueError("At least one image is required for carousel posts")
# #             if isinstance(v, str):
# #                 return [v]
# #             if not all(isinstance(url, str) and re.match(r'^https://res\.cloudinary\.com/.*', url) for url in v):
# #                 raise ValueError("All image URLs must be valid Cloudinary URLs")
# #         else:
# #             if v and isinstance(v, list):
# #                 raise ValueError("Single post cannot have multiple images")
# #             if v and not re.match(r'^https://res\.cloudinary\.com/.*', v):
# #                 raise ValueError("Image URL must be a valid Cloudinary URL")
# #         return v
# #
# # @router.post("/save-draft/", status_code=status.HTTP_201_CREATED)
# # async def save_draft(draft: DraftCreate):
# #     try:
# #         draft_data = draft.dict()
# #         draft_data["created_at"] = datetime.utcnow()
# #
# #         result = drafts_collection.insert_one(draft_data)
# #
# #         return {
# #             "status": "success",
# #             "message": "Draft saved successfully",
# #             "draft_id": str(result.inserted_id)
# #         }
# #
# #     except Exception as e:
# #         logger.error(f"Draft save error: {str(e)}")
# #         raise HTTPException(
# #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
# #             detail={
# #                 "status": "error",
# #                 "message": "Failed to save draft",
# #                 "error": str(e)
# #             }
# #         )
# #
# # @router.get("/get-drafts/", response_model=List[dict])
# # async def get_drafts():
# #     try:
# #         drafts = []
# #         for draft in drafts_collection.find().sort("created_at", -1).limit(50):
# #             draft["_id"] = str(draft["_id"])
# #             draft["created_at"] = draft["created_at"].isoformat()
# #             drafts.append(draft)
# #         return {
# #             "status": "success",
# #             "data": drafts,
# #             "total": len(drafts)
# #         }
# #     except Exception as e:
# #         logger.error(f"Get drafts error: {str(e)}")
# #         raise HTTPException(
# #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
# #             detail={
# #                 "status": "error",
# #                 "message": "Failed to fetch drafts",
# #                 "error": str(e)
# #             }
# #         )
# #
# # @router.delete("/delete-draft/{draft_id}", status_code=status.HTTP_200_OK)
# # async def delete_draft(draft_id: str):
# #     try:
# #         result = drafts_collection.delete_one({"_id": ObjectId(draft_id)})
# #         if result.deleted_count == 0:
# #             raise HTTPException(
# #                 status_code=status.HTTP_404_NOT_FOUND,
# #                 detail={
# #                     "status": "error",
# #                     "message": "Draft not found"
# #                 }
# #             )
# #         return {
# #             "status": "success",
# #             "message": "Draft deleted successfully"
# #         }
# #     except Exception as e:
# #         logger.error(f"Delete draft error: {str(e)}")
# #         raise HTTPException(
# #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
# #             detail={
# #                 "status": "error",
# #                 "message": "Failed to delete draft",
# #                 "error": str(e)
# #             }
# #         )
# #
# # @router.get("/get-drafts/", response_model=dict)
# # async def get_drafts(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
# #     try:
# #         skip = (page - 1) * limit
# #         drafts = []
# #         total = drafts_collection.count_documents({})
# #         for draft in drafts_collection.find().sort("created_at", -1).skip(skip).limit(limit):
# #             draft["_id"] = str(draft["_id"])
# #             draft["created_at"] = draft["created_at"].isoformat()
# #             drafts.append(draft)
# #         return {
# #             "status": "success",
# #             "data": drafts,
# #             "total": total,
# #             "page": page,
# #             "limit": limit,
# #             "pages": (total + limit - 1) // limit
# #         }
# #     except Exception as e:
# #         logger.error(f"Get drafts error: {str(e)}")
# #         raise HTTPException(
# #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
# #             detail={
# #                 "status": "error",
# #                 "message": "Failed to fetch drafts",
# #                 "error": str(e)
# #             }
# #         )
#
# from fastapi import APIRouter, HTTPException, status, Query
# from pydantic import BaseModel, Field, validator
# from datetime import datetime
# from typing import List, Optional, Union
# from app.database import drafts_collection
# import logging
# import re
# from bson import ObjectId
#
# router = APIRouter()
#
# logger = logging.getLogger(__name__)
#
# class DraftCreate(BaseModel):
#     caption: str = Field(..., min_length=1, max_length=2200)
#     platform: str = Field(..., pattern=r"^(instagram|facebook|twitter|linkedin)$")
#     image_url: Optional[Union[str, List[str]]] = None
#     prompt: Optional[str] = Field(None, max_length=500)
#     is_carousel: bool = False
#
#     @validator('image_url')
#     def validate_image_url(cls, v, values):
#         if values.get('is_carousel'):
#             if v is None or (isinstance(v, list) and not v):
#                 return v  # Allow empty image_url for drafts
#             if isinstance(v, str):
#                 v = [v]
#             if not all(isinstance(url, str) and re.match(r'^https?://.*cloudinary\.com/.*', url) for url in v):
#                 raise ValueError("All image URLs must be valid Cloudinary URLs")
#             return v
#         else:
#             if v and isinstance(v, list):
#                 raise ValueError("Single post cannot have multiple images")
#             if v and not re.match(r'^https?://.*cloudinary\.com/.*', v):
#                 raise ValueError("Image URL must be a valid Cloudinary URL")
#             return v
#
# @router.post("/save-draft/", status_code=status.HTTP_201_CREATED)
# async def save_draft(draft: DraftCreate):
#     try:
#         draft_data = draft.dict()
#         logger.info(f"Received draft data: {draft_data}")
#         draft_data["created_at"] = datetime.utcnow()
#
#         result = drafts_collection.insert_one(draft_data)
#
#         return {
#             "status": "success",
#             "message": "Draft saved successfully",
#             "draft_id": str(result.inserted_id)
#         }
#     except Exception as e:
#         logger.error(f"Draft save error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail={
#                 "status": "error",
#                 "message": "Failed to save draft",
#                 "error": str(e)
#             }
#         )
#
# @router.get("/get-drafts/", response_model=dict)
# async def get_drafts(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
#     try:
#         skip = (page - 1) * limit
#         drafts = []
#         total = drafts_collection.count_documents({})
#         for draft in drafts_collection.find().sort("created_at", -1).skip(skip).limit(limit):
#             draft["_id"] = str(draft["_id"])
#             draft["created_at"] = draft["created_at"].isoformat()
#             drafts.append(draft)
#         return {
#             "status": "success",
#             "data": drafts,
#             "total": total,
#             "page": page,
#             "limit": limit,
#             "pages": (total + limit - 1) // limit
#         }
#     except Exception as e:
#         logger.error(f"Get drafts error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail={
#                 "status": "error",
#                 "message": "Failed to fetch drafts",
#                 "error": str(e)
#             }
#         )
#
# @router.delete("/delete-draft/{draft_id}", status_code=status.HTTP_200_OK)
# async def delete_draft(draft_id: str):
#     try:
#         result = drafts_collection.delete_one({"_id": ObjectId(draft_id)})
#         if result.deleted_count == 0:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail={
#                     "status": "error",
#                     "message": "Draft not found"
#                 }
#             )
#         return {
#             "status": "success",
#             "message": "Draft deleted successfully"
#         }
#     except Exception as e:
#         logger.error(f"Delete draft error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail={
#                 "status": "error",
#                 "message": "Failed to delete draft",
#                 "error": str(e)
#             }
#         )

from fastapi import APIRouter, HTTPException, status, Query, Request
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional, Union
from app.database import drafts_collection
import logging
import re
from bson import ObjectId

router = APIRouter()

logger = logging.getLogger(__name__)
logger.info("Loading drafts.py version with pre=True is_carousel validator and raw body logging")


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
async def save_draft(request: Request, draft: DraftCreate):
    try:
        raw_body = await request.body()
        logger.info(f"Raw request body: {raw_body.decode('utf-8')}")
        draft_data = draft.dict()
        logger.info(f"Received draft data: {draft_data}")
        draft_data["created_at"] = datetime.utcnow()

        # Add await here
        result = await drafts_collection.insert_one(draft_data)
        logger.info(f"Draft saved successfully with ID: {result.inserted_id}")

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
async def get_drafts(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    try:
        skip = (page - 1) * limit
        # Add await for count_documents
        total = await drafts_collection.count_documents({})

        # Get cursor and convert to list
        cursor = drafts_collection.find().sort("created_at", -1).skip(skip).limit(limit)
        drafts = await cursor.to_list(length=None)

        # Process results
        for draft in drafts:
            draft["_id"] = str(draft["_id"])
            draft["created_at"] = draft["created_at"].isoformat() if isinstance(draft["created_at"], datetime) else \
            draft["created_at"]

        return {
            "status": "success",
            "data": drafts,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        logger.error(f"Get drafts error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to fetch drafts",
                "error": str(e)
            }
        )

@router.delete("/delete-draft/{draft_id}", status_code=status.HTTP_200_OK)
async def delete_draft(draft_id: str):
    try:
        # Add await here
        result = await drafts_collection.delete_one({"_id": ObjectId(draft_id)})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "status": "error",
                    "message": "Draft not found"
                }
            )
        return {
            "status": "success",
            "message": "Draft deleted successfully"
        }
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