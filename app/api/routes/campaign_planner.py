
import traceback
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.services.content_planner_engine import generate_content_plan
router = APIRouter()

# @router.post("/plan-campaign/")
# async def plan_campaign(data: dict):
#     try:
#         result = generate_content_plan(
#             campaign_name=data["name"],
#             theme=data["theme"],
#             count=data["count"]
#         )
#         return {"content": result}  # ✅ Rename "result" to "content"
#     except Exception as e:
#         traceback_str = traceback.format_exc()
#         print("ERROR in /plan-campaign/:", traceback_str)
#         return JSONResponse(
#             status_code=500,
#             content={"error": str(e), "trace": traceback_str}
#         )

@router.post("/plan-campaign/")
async def plan_campaign(data: dict):
    try:
        result = generate_content_plan(
            campaign_name=data["name"],
            theme=data["theme"],
            count=data["count"],
            start_date=data["startDate"],
            end_date=data["endDate"]
        )
        return {"content": result}
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("ERROR in /plan-campaign/:", traceback_str)
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "trace": traceback_str}
        )
