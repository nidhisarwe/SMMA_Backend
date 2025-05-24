# app/api/routes/campaign_schedules.py - FIXED VERSION WITH PROPER POST GENERATION
from fastapi import APIRouter, HTTPException, Depends, status
from app.database import campaign_schedules_collection, scheduled_posts_collection
from app.api.dependencies import auth_required
from datetime import datetime, timedelta
from bson import ObjectId
from typing import List, Optional
import traceback

router = APIRouter()

@router.get("/get-campaigns")
async def get_all_campaigns(current_user_id: str = Depends(auth_required)):
    """
    Get all campaigns for the authenticated user.
    This endpoint is specifically for the SavedCampaigns page.
    """
    try:
        cursor = campaign_schedules_collection.find({"user_id": current_user_id}).sort("created_at", -1)
        campaigns = await cursor.to_list(length=100)

        formatted_campaigns = []
        for campaign in campaigns:
            # Count actual posts in scheduled_posts collection for this campaign
            posts_count = await scheduled_posts_collection.count_documents({
                "campaign_id": str(campaign["_id"]),
                "user_id": current_user_id
            })

            # Get parsed_posts from different possible locations in the campaign data
            parsed_posts = []
            if "parsed_posts" in campaign and isinstance(campaign["parsed_posts"], list):
                parsed_posts = campaign["parsed_posts"]
                print(f"Found {len(parsed_posts)} parsed_posts in campaign {campaign.get('campaign_name')}")
            elif "content" in campaign and isinstance(campaign["content"], dict) and "parsed_posts" in campaign["content"]:
                parsed_posts = campaign["content"]["parsed_posts"]
                print(f"Found {len(parsed_posts)} parsed_posts in campaign.content for {campaign.get('campaign_name')}")

            formatted_campaign = {
                "_id": str(campaign["_id"]),
                "campaign_name": campaign.get("campaign_name", campaign.get("name", "Untitled Campaign")),
                "theme": campaign.get("theme", ""),
                "start_date": campaign.get("start_date"),
                "end_date": campaign.get("end_date"),
                "status": campaign.get("status", "draft"),
                "created_at": campaign.get("created_at"),
                "updated_at": campaign.get("updated_at"),
                "user_id": campaign.get("user_id"),
                "posts": campaign.get("posts", []),
                "parsed_posts": parsed_posts,  # Include parsed_posts in the response
                "post_count": len(parsed_posts) if parsed_posts else posts_count  # Use parsed_posts count if available
            }
            formatted_campaigns.append(formatted_campaign)

        return formatted_campaigns

    except Exception as e:
        print(f"Error getting campaigns: {e}")
        traceback_str = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching campaigns: {str(e)}"
        )

@router.get("/get-campaign/{campaign_id}")
async def get_campaign_schedule_by_id(campaign_id: str, current_user_id: str = Depends(auth_required)):
    """
    Get a specific campaign by ID (endpoint that CampaignPage.jsx expects).
    """
    try:
        try:
            campaign_obj_id = ObjectId(campaign_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid campaign ID format"
            )

        campaign = await campaign_schedules_collection.find_one({
            "_id": campaign_obj_id,
            "user_id": current_user_id
        })

        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found or you don't have permission to access it"
            )

        campaign["id"] = str(campaign.pop("_id"))

        if isinstance(campaign.get("created_at"), datetime):
            campaign["created_at"] = campaign["created_at"].isoformat()
        if isinstance(campaign.get("updated_at"), datetime):
            campaign["updated_at"] = campaign["updated_at"].isoformat()

        return campaign

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error getting campaign {campaign_id}: {e}")
        traceback_str = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the campaign: {str(e)}"
        )

@router.post("/generate-content/{campaign_id}")
async def generate_campaign_content(campaign_id: str, current_user_id: str = Depends(auth_required)):
    """
    Generate content for an existing campaign but DO NOT automatically create scheduled posts.
    Posts will be stored in the campaign document but not scheduled on the calendar.
    """
    try:
        try:
            campaign_obj_id = ObjectId(campaign_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid campaign ID format"
            )

        campaign = await campaign_schedules_collection.find_one({
            "_id": campaign_obj_id,
            "user_id": current_user_id
        })

        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found or you don't have permission to access it"
            )

        # We'll no longer automatically create scheduled posts
        # Instead, we'll just update the campaign status

        # Check if the campaign has parsed_posts
        if not campaign.get("parsed_posts"):
            # If no parsed_posts, we can't do anything
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campaign has no content to generate posts from"
            )

        # Log that we're not automatically scheduling posts
        print(f"Campaign {campaign_id} has {len(campaign.get('parsed_posts', []))} posts ready to be scheduled manually")

        # Update campaign status to active
        await campaign_schedules_collection.update_one(
            {"_id": campaign_obj_id, "user_id": current_user_id},
            {
                "$set": {
                    "status": "active",
                    "updated_at": datetime.utcnow()
                }
            }
        )

        return {"message": "Content generated and posts scheduled successfully for campaign"}

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error generating content: {e}")
        traceback_str = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating content: {str(e)}"
        )

@router.post("/campaigns")
async def create_campaign(campaign_data: dict, current_user_id: str = Depends(auth_required)):
    """
    Create a new campaign for the authenticated user.
    """
    try:
        if not campaign_data.get("name"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campaign name is required"
            )

        new_campaign = {
            "campaign_name": campaign_data["name"],
            "theme": campaign_data.get("theme", ""),
            "start_date": campaign_data.get("start_date"),
            "end_date": campaign_data.get("end_date"),
            "user_id": current_user_id,
            "status": campaign_data.get("status", "draft"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "posts": [],
            "post_count": 0
        }

        result = await campaign_schedules_collection.insert_one(new_campaign)

        created_campaign = await campaign_schedules_collection.find_one({"_id": result.inserted_id})
        created_campaign["id"] = str(created_campaign.pop("_id"))

        return created_campaign

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error creating campaign: {e}")
        traceback_str = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the campaign: {str(e)}"
        )

@router.put("/campaigns/{campaign_id}")
async def update_campaign(campaign_id: str, campaign_data: dict, current_user_id: str = Depends(auth_required)):
    """
    Update a campaign, ensuring it belongs to the authenticated user.
    """
    try:
        try:
            campaign_obj_id = ObjectId(campaign_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid campaign ID format"
            )

        existing_campaign = await campaign_schedules_collection.find_one({
            "_id": campaign_obj_id,
            "user_id": current_user_id
        })

        if not existing_campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found or you don't have permission to update it"
            )

        update_data = {
            "updated_at": datetime.utcnow()
        }

        if "name" in campaign_data:
            update_data["campaign_name"] = campaign_data["name"]
        if "theme" in campaign_data:
            update_data["theme"] = campaign_data["theme"]
        if "start_date" in campaign_data:
            update_data["start_date"] = campaign_data["start_date"]
        if "end_date" in campaign_data:
            update_data["end_date"] = campaign_data["end_date"]
        if "status" in campaign_data:
            update_data["status"] = campaign_data["status"]

        await campaign_schedules_collection.update_one(
            {"_id": campaign_obj_id, "user_id": current_user_id},
            {"$set": update_data}
        )

        updated_campaign = await campaign_schedules_collection.find_one({
            "_id": campaign_obj_id,
            "user_id": current_user_id
        })
        updated_campaign["id"] = str(updated_campaign.pop("_id"))

        if isinstance(updated_campaign.get("created_at"), datetime):
            updated_campaign["created_at"] = updated_campaign["created_at"].isoformat()
        if isinstance(updated_campaign.get("updated_at"), datetime):
            updated_campaign["updated_at"] = updated_campaign["updated_at"].isoformat()

        return updated_campaign

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error updating campaign: {e}")
        traceback_str = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the campaign: {str(e)}"
        )

@router.delete("/delete-campaign/{campaign_id}")
async def delete_campaign(campaign_id: str, current_user_id: str = Depends(auth_required)):
    """
    Delete a campaign, ensuring it belongs to the authenticated user.
    Also deletes all associated posts.
    """
    try:
        try:
            campaign_obj_id = ObjectId(campaign_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid campaign ID format"
            )

        existing_campaign = await campaign_schedules_collection.find_one({
            "_id": campaign_obj_id,
            "user_id": current_user_id
        })

        if not existing_campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found or you don't have permission to delete it"
            )

        # Delete all associated posts first
        deleted_posts_result = await scheduled_posts_collection.delete_many({
            "campaign_id": campaign_id,
            "user_id": current_user_id
        })

        # Delete the campaign
        await campaign_schedules_collection.delete_one({
            "_id": campaign_obj_id,
            "user_id": current_user_id
        })

        return {
            "message": f"Campaign deleted successfully along with {deleted_posts_result.deleted_count} associated posts"
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error deleting campaign: {e}")
        traceback_str = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the campaign: {str(e)}"
        )