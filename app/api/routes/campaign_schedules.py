from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.database import campaign_schedules_collection
from bson import ObjectId

router = APIRouter()


# 🧩 Models
class CampaignPost(BaseModel):
    title: str
    type: str
    schedule: str
    description: str
    cta: str


class CampaignPayload(BaseModel):
    campaignName: str
    theme: str
    posts: List[CampaignPost]
    startDate: str
    endDate: str


# 🚀 Save a Campaign
@router.get("/get-campaigns")
async def get_all_campaigns():
    try:
        # Update to use Motor's async cursor
        cursor = campaign_schedules_collection.find().sort("created_at", -1)
        campaigns = await cursor.to_list(length=None)

        for campaign in campaigns:
            campaign["_id"] = str(campaign["_id"])
            if "created_at" in campaign and isinstance(campaign["created_at"], datetime):
                campaign["created_at"] = campaign["created_at"].isoformat()
        return campaigns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-campaign/{campaign_id}")
async def get_campaign(campaign_id: str):
    try:
        campaign = await campaign_schedules_collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        campaign["_id"] = str(campaign["_id"])
        if "created_at" in campaign and isinstance(campaign["created_at"], datetime):
            campaign["created_at"] = campaign["created_at"].isoformat()

        return campaign
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/save-campaign/")
async def save_campaign(payload: CampaignPayload):
    try:
        campaign_data = {
            "campaign_name": payload.campaignName,
            "theme": payload.theme,
            "posts": [post.dict() for post in payload.posts],
            "start_date": payload.startDate,
            "end_date": payload.endDate,
            "created_at": datetime.utcnow()
        }

        # Add await here
        result = await campaign_schedules_collection.insert_one(campaign_data)

        return {
            "message": "Campaign schedule saved successfully!",
            "campaign_id": str(result.inserted_id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-campaign/{campaign_id}")
async def delete_campaign(campaign_id: str):
    try:
        # Add await here
        result = await campaign_schedules_collection.delete_one({"_id": ObjectId(campaign_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return {"message": "Campaign deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))