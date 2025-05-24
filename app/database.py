from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI",
                      "mongodb+srv://social2sync:12345@cluster0.ewalfva.mongodb.net/social_sync_db?retryWrites=true&w=majority")

client = AsyncIOMotorClient(MONGO_URI)
db = client["social_sync_db"]

# Collections
users_collection = db["users"]
drafts_collection = db["drafts"]
campaign_schedules_collection = db["campaign_schedules"]
scheduled_posts_collection = db["scheduled_posts"]
connected_accounts_collection = db["connected_accounts"]
password_reset_tokens_collection = db["password_reset_tokens"]


async def create_indexes():
    # User email index
    await users_collection.create_index("email", unique=True)

    # Password reset token index with TTL (tokens expire after 1 hour)
    await password_reset_tokens_collection.create_index(
        "created_at",
        expireAfterSeconds=3600  # 1 hour
    )
    await password_reset_tokens_collection.create_index(
        "token",
        unique=True
    )

    print("Database indexes ensured.")


__all__ = [
    "users_collection",
    "drafts_collection",
    "campaign_schedules_collection",
    "scheduled_posts_collection",
    "connected_accounts_collection",
    "password_reset_tokens_collection",
    "create_indexes",
    "db"
]