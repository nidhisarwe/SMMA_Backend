# # backend/app/services/auth_service.py
# from pymongo.errors import DuplicateKeyError
# from fastapi import HTTPException, status
# from app.models.user import UserCreate
# from app.core.security import get_password_hash, verify_password
# from app.database import users_collection  # Make sure users_collection is imported from your database.py
# from typing import Optional
# from datetime import datetime
# async def create_new_user(user_data: UserCreate) -> dict:
#     """
#     Creates a new user in the database.
#     Hashes the password before storing.
#     Returns the created user data as a dictionary (including its new ID).
#     """
#     hashed_password = get_password_hash(user_data.password)
#
#     user_db_dict = {
#         "full_name": user_data.full_name,
#         "email": user_data.email,
#         "organization_name": user_data.organization_name,
#         "hashed_password": hashed_password,
#         "created_at": datetime.utcnow(),  # <--- MAKE SURE THIS IS SET
#         "connected_accounts": [],  # <--- Initialize if needed
#         "last_login": None  # <--- Initialize if needed
#     }
#
#     try:
#         result = await users_collection.insert_one(user_db_dict)
#         created_user = await users_collection.find_one({"_id": result.inserted_id})
#         if created_user:
#             created_user["id"] = str(created_user["_id"])  # Convert ObjectId to string for 'id'
#             return created_user
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                             detail="Failed to retrieve user after creation.")
#     except DuplicateKeyError:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")
#     except Exception as e:
#         # Log the exception e for debugging
#         print(f"Error creating user: {e}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                             detail="An unexpected error occurred during user creation.")
#
#
# async def verify_user_credentials(email: str, password: str) -> Optional[dict]:
#     user_db_doc = await users_collection.find_one({"email": email})
#     if not user_db_doc:
#         return None
#     if not verify_password(password, user_db_doc["hashed_password"]):
#         return None
#
#     user_db_doc["id"] = str(user_db_doc.pop("_id"))  # Convert _id to id and remove original _id
#
#     # Ensure 'created_at' is present, if not, this indicates an issue with data from when user was created
#     if "created_at" not in user_db_doc:
#         # This is problematic. created_at should exist.
#         # For now, one might raise an error or provide a default, but it's better to ensure it's in the DB.
#         # print(f"Warning: 'created_at' field missing for user {email}. This should not happen.")
#         # user_db_doc["created_at"] = datetime.utcnow() # Fallback, not ideal
#         pass  # Or handle as an error
#
#     # Ensure 'connected_accounts' is present, provide default if missing
#     if "connected_accounts" not in user_db_doc:
#         user_db_doc["connected_accounts"] = []
#
#     # Ensure 'last_login' is present or set to None if missing
#     if "last_login" not in user_db_doc:
#         user_db_doc["last_login"] = None
#
#     return user_db_doc

from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException, status
from app.models.user import UserCreate, PasswordResetRequest, PasswordReset
from app.core.security import get_password_hash, verify_password
from app.database import users_collection, password_reset_tokens_collection
from typing import Optional
from datetime import datetime
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()


async def create_new_user(user_data: UserCreate) -> dict:
    hashed_password = get_password_hash(user_data.password)
    user_db_dict = {
        "full_name": user_data.full_name,
        "email": user_data.email,
        "organization_name": user_data.organization_name,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "connected_accounts": [],
        "last_login": None
    }
    try:
        result = await users_collection.insert_one(user_db_dict)
        created_user = await users_collection.find_one({"_id": result.inserted_id})
        if created_user:
            created_user["id"] = str(created_user["_id"])
            return created_user
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user after creation."
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists."
        )
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during user creation."
        )


async def verify_user_credentials(email: str, password: str) -> Optional[dict]:
    user_db_doc = await users_collection.find_one({"email": email})
    if not user_db_doc:
        return None
    if not verify_password(password, user_db_doc["hashed_password"]):
        return None
    user_db_doc["id"] = str(user_db_doc.pop("_id"))
    if "connected_accounts" not in user_db_doc:
        user_db_doc["connected_accounts"] = []
    if "last_login" not in user_db_doc:
        user_db_doc["last_login"] = None
    return user_db_doc


async def request_password_reset(reset_request: PasswordResetRequest) -> dict:
    user = await users_collection.find_one({"email": reset_request.email})
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email is registered, a reset link has been sent."}

    # Generate unique token
    token = str(uuid.uuid4())
    reset_doc = {
        "token": token,
        "user_id": user["_id"],
        "email": reset_request.email,
        "created_at": datetime.utcnow()
    }

    try:
        await password_reset_tokens_collection.insert_one(reset_doc)
    except DuplicateKeyError:
        # Rare case, regenerate token
        token = str(uuid.uuid4())
        reset_doc["token"] = token
        await password_reset_tokens_collection.insert_one(reset_doc)

    # Send email
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    app_url = os.getenv("APP_URL", "http://localhost:5173")

    reset_link = f"{app_url}/reset-password?token={token}"
    subject = "SocialSync Password Reset Request"
    body = f"""
    Hello,

    You requested to reset your SocialSync password. Click the link below to set a new password:
    {reset_link}

    This link will expire in 1 hour.

    Best regards,
    SocialSync Team
    """

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = reset_request.email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reset email."
        )

    return {"message": "If the email is registered, a reset link has been sent."}


async def reset_password(reset_data: PasswordReset) -> dict:
    token_doc = await password_reset_tokens_collection.find_one({"token": reset_data.token})
    if not token_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token."
        )

    user = await users_collection.find_one({"_id": token_doc["user_id"]})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found."
        )

    # Update password
    hashed_password = get_password_hash(reset_data.new_password)
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"hashed_password": hashed_password}}
    )

    # Invalidate token
    await password_reset_tokens_collection.delete_one({"token": reset_data.token})

    return {"message": "Password reset successfully."}