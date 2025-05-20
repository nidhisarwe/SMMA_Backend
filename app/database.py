# # # # from pymongo import MongoClient
# # # #
# # # # MONGO_URI = "mongodb+srv://mhtcetnavigator410:nGfvHhyj9rnkD5S1@cluster0.pwyhww6.mongodb.net/social_sync_db?retryWrites=true&w=majority"
# # # #
# # # # client = MongoClient(MONGO_URI)
# # # # db = client["social_sync_db"]
# # # #
# # # # # Existing collections
# # # # drafts_collection = db["drafts"]
# # # # # New collection for campaign schedules
# # # # campaign_schedules_collection = db["campaign_schedules"]
# # #
# # # # database.py
# # # from pymongo import MongoClient
# # #
# # # MONGO_URI = "mongodb+srv://mhtcetnavigator410:nGfvHhyj9rnkD5S1@cluster0.pwyhww6.mongodb.net/social_sync_db?retryWrites=true&w=majority"
# # #
# # # client = MongoClient(MONGO_URI)
# # # db = client["social_sync_db"]
# # #
# # # # Collections
# # # drafts_collection = db["drafts"]
# # # campaign_schedules_collection = db["campaign_schedules"]
# # # users_collection = db["users"]  # Add other collections you need
# # #
# # # # Export collections
# # # __all__ = ['drafts_collection', 'campaign_schedules_collection', 'users_collection']
# # #
# # # # database.py
# # # from pymongo import MongoClient
# # # from datetime import datetime
# # # import os
# # # from dotenv import load_dotenv
# # #
# # # MONGO_URI = "mongodb+srv://mhtcetnavigator410:nGfvHhyj9rnkD5S1@cluster0.pwyhww6.mongodb.net/social_sync_db?retryWrites=true&w=majority"
# # #
# # # client = MongoClient(MONGO_URI)
# # # db = client["social_sync_db"]
# # #
# # # # Collections
# # # users_collection = db["users"]
# # # drafts_collection = db["drafts"]
# # # campaign_schedules_collection = db["campaign_schedules"]
# # # scheduled_posts_collection = db["scheduled_posts"]
# # # connected_accounts_collection = db["connected_accounts"]
# # # # Indexes
# # # users_collection.create_index("email", unique=True)
# # # # Allow multiple LinkedIn accounts (personal and company) per user
# # # connected_accounts_collection.create_index([
# # #     ("user_id", 1),
# # #     ("platform", 1),
# # #     ("account_id", 1)  # Add account_id to make sure different LinkedIn accounts can be stored
# # # ], unique=True)
# # #
# # # # Indexes
# # # users_collection.create_index("email", unique=True)
# # # connected_accounts_collection.create_index([("user_id", 1), ("platform", 1)], unique=True)
# # #
# # # __all__ = [
# # #     "users_collection",
# # #     "drafts_collection",
# # #     "campaign_schedules_collection",
# # #     "scheduled_posts_collection",
# # #     "connected_accounts_collection"
# # # ]
# #
# #
# #
# #
# # # database.py
# # from motor.motor_asyncio import AsyncIOMotorClient
# # from datetime import datetime
# # import os
# # from dotenv import load_dotenv
# #
# # # Load environment variables
# # load_dotenv()
# #
# # MONGO_URI = "mongodb+srv://mhtcetnavigator410:nGfvHhyj9rnkD5S1@cluster0.pwyhww6.mongodb.net/social_sync_db?retryWrites=true&w=majority"
# #
# # # Use AsyncIOMotorClient for async MongoDB operations
# # client = AsyncIOMotorClient(MONGO_URI)
# # db = client["social_sync_db"]
# #
# # # Collections
# # users_collection = db["users"]
# # drafts_collection = db["drafts"]
# # campaign_schedules_collection = db["campaign_schedules"]
# # scheduled_posts_collection = db["scheduled_posts"]
# # connected_accounts_collection = db["connected_accounts"]
# #
# # # Create indexes function to be called during app startup
# # async def create_indexes():
# #     await users_collection.create_index("email", unique=True)
# #     # Allow multiple LinkedIn accounts (personal and company) per user
# #     await connected_accounts_collection.create_index([
# #         ("user_id", 1),
# #         ("platform", 1),
# #         ("account_id", 1)  # Add account_id to make sure different LinkedIn accounts can be stored
# #     ], unique=True)
# #
# # # Export collections
# # __all__ = [
# #     "users_collection",
# #     "drafts_collection",
# #     "campaign_schedules_collection",
# #     "scheduled_posts_collection",
# #     "connected_accounts_collection",
# #     "create_indexes"
# # ]
#
#
# # backend/app/database.py
# from motor.motor_asyncio import AsyncIOMotorClient
# import os
# from dotenv import load_dotenv
#
# load_dotenv()
#
# MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://mhtcetnavigator410:nGfvHhyj9rnkD5S1@cluster0.pwyhww6.mongodb.net/social_sync_db?retryWrites=true&w=majority") # Fallback if not in .env
#
# client = AsyncIOMotorClient(MONGO_URI)
# db = client["social_sync_db"] # Or your database name
#
# # Collections
# users_collection = db["users"]
# drafts_collection = db["drafts"]
# campaign_schedules_collection = db["campaign_schedules"]
# scheduled_posts_collection = db["scheduled_posts"]
# connected_accounts_collection = db["connected_accounts"]
#
# async def create_indexes():
#     await users_collection.create_index("email", unique=True)
#     # Example for another collection if needed:
#     # await connected_accounts_collection.create_index(
#     #     [("user_id", 1), ("platform", 1), ("account_id", 1)], unique=True
#     # )
#     print("Database indexes ensured.")
#
# # Export collections and functions
# __all__ = [
#     "users_collection",
#     "drafts_collection",
#     "campaign_schedules_collection",
#     "scheduled_posts_collection",
#     "connected_accounts_collection",
#     "create_indexes",
#     "db" # Export db if other modules need it directly
# ]

from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI",
                      "mongodb+srv://mhtcetnavigator410:nGfvHhyj9rnkD5S1@cluster0.pwyhww6.mongodb.net/social_sync_db?retryWrites=true&w=majority")

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