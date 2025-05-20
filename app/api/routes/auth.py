# # backend/app/api/routes/auth.py
# from fastapi import APIRouter, HTTPException, status
# from app.models.user import UserCreate, UserLogin, UserViewModel
# from app.services.auth_service import create_new_user, verify_user_credentials
# from app.database import users_collection  # <-- Import users_collection
# from bson import ObjectId  # <-- Import ObjectId
# from datetime import datetime
#
# router = APIRouter()
#
#
# @router.post("/register", response_model=UserViewModel, status_code=status.HTTP_201_CREATED)
# async def register_user(user_in: UserCreate):
#     try:
#         created_user_dict = await create_new_user(user_in)
#         # created_user_dict should already have 'id', 'created_at', 'connected_accounts' etc.
#         # as prepared by create_new_user service
#         return UserViewModel(**created_user_dict)
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         print(f"Unexpected error during registration: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="An unexpected error occurred during registration."
#         )
#
#
# @router.post("/login")  # Removed response_model here as it's part of the dict
# async def login_user(form_data: UserLogin):
#     user_dict_from_db = await verify_user_credentials(email=form_data.email, password=form_data.password)
#
#     if not user_dict_from_db:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password.",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#
#     current_time = datetime.utcnow()
#     try:
#         # user_dict_from_db["id"] should be the string version of _id
#         await users_collection.update_one(
#             {"_id": ObjectId(user_dict_from_db["id"])},
#             {"$set": {"last_login": current_time}}
#         )
#         user_dict_from_db["last_login"] = current_time  # Update the dict for UserViewModel
#     except Exception as e:
#         print(f"Error updating last_login: {e}")
#         # Decide if this should be a critical error or just a warning
#
#     # At this point, user_dict_from_db should have:
#     # id, email, full_name, organization_name, created_at, last_login, connected_accounts
#     # All of these are needed by UserViewModel (or have defaults)
#
#     try:
#         user_view = UserViewModel(**user_dict_from_db)
#     except Exception as pydantic_error:
#         print(f"Pydantic validation error during login: {pydantic_error}")
#         print(f"Data passed to UserViewModel: {user_dict_from_db}")
#         raise HTTPException(
#             status_code=500,
#             detail="Internal server error: Could not process user data."
#         )
#
#     return {
#         "message": "Login successful!",
#         "user": user_view  # Pass the validated UserViewModel instance
#     }

from fastapi import APIRouter, HTTPException, status
from app.models.user import UserCreate, UserLogin, UserViewModel, PasswordResetRequest, PasswordReset
from app.services.auth_service import create_new_user, verify_user_credentials, request_password_reset, reset_password
from app.database import users_collection
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/register", response_model=UserViewModel, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate):
    try:
        created_user_dict = await create_new_user(user_in)
        return UserViewModel(**created_user_dict)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration."
        )

@router.post("/login")
async def login_user(form_data: UserLogin):
    user_dict_from_db = await verify_user_credentials(email=form_data.email, password=form_data.password)
    if not user_dict_from_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    current_time = datetime.utcnow()
    try:
        await users_collection.update_one(
            {"_id": ObjectId(user_dict_from_db["id"])},
            {"$set": {"last_login": current_time}}
        )
        user_dict_from_db["last_login"] = current_time
    except Exception as e:
        print(f"Error updating last_login: {e}")
    try:
        user_view = UserViewModel(**user_dict_from_db)
    except Exception as pydantic_error:
        print(f"Pydantic validation error during login: {pydantic_error}")
        print(f"Data passed to UserViewModel: {user_dict_from_db}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error: Could not process user data."
        )
    return {
        "message": "Login successful!",
        "user": user_view
    }

@router.post("/forgot-password")
async def forgot_password(reset_request: PasswordResetRequest):
    try:
        result = await request_password_reset(reset_request)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error processing password reset request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )

@router.post("/reset-password")
async def reset_password_endpoint(reset_data: PasswordReset):
    try:
        result = await reset_password(reset_data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error resetting password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )