# # from enum import Enum
# # from typing import List, Optional
# # from pydantic import BaseModel, Field
# # from datetime import datetime
# #
# # class SocialPlatform(str, Enum):
# #     INSTAGRAM = "instagram"
# #     FACEBOOK = "facebook"
# #     LINKEDIN = "linkedin"
# #     TWITTER = "twitter"
# #
# # class ConnectedAccount(BaseModel):
# #     platform: SocialPlatform
# #     name: str
# #     email: Optional[str] = None
# #     profile_picture: Optional[str] = None
# #     access_token: str
# #     refresh_token: Optional[str] = None
# #     expires_in: Optional[datetime] = None
# #     account_id: str
# #     account_type: str = "personal"  # "personal" or "company"
# #     is_active: bool = True
# #     connected_at: datetime = Field(default_factory=datetime.utcnow)
# #
# # class User(BaseModel):
# #     email: str
# #     name: str
# #     connected_accounts: List[ConnectedAccount] = []
# #     created_at: datetime = Field(default_factory=datetime.utcnow)
# #     last_login: Optional[datetime] = None
#
# # backend/app/models/user.py
#
# from enum import Enum
# from typing import List, Optional
# from pydantic import BaseModel, EmailStr, Field
# from datetime import datetime
#
#
# # --- Social Account Details ---
#
# class SocialPlatform(str, Enum):
#     INSTAGRAM = "instagram"
#     FACEBOOK = "facebook"
#     LINKEDIN = "linkedin"
#     TWITTER = "twitter"
#     # Add other platforms as needed, e.g., TIKTOK = "tiktok"
#
#
# class ConnectedAccount(BaseModel):
#     platform: SocialPlatform
#     account_id: str  # Platform-specific ID for the user/page on that platform
#     name: str  # Profile name or page name on the platform
#     email: Optional[EmailStr] = None  # Email associated with the platform account, if available
#     profile_picture: Optional[str] = None  # URL to the profile picture
#
#     # Sensitive tokens - ensure these are stored securely (e.g., encrypted at rest)
#     access_token: str
#     refresh_token: Optional[str] = None
#     expires_in: Optional[datetime] = None  # Timestamp when the access_token expires
#
#     account_type: str = "personal"  # e.g., "personal", "page", "company_profile"
#     is_active: bool = True  # Whether this connection is currently active for posting/fetching
#     connected_at: datetime = Field(default_factory=datetime.utcnow)
#
#     # You might add last_synced_at, permissions/scopes, etc.
#
#     class Config:
#         use_enum_values = True  # Serializes enums to their values (e.g., "instagram")
#         json_encoders = {
#             datetime: lambda dt: dt.isoformat()  # Consistent datetime string format
#         }
#
#
# # --- User Authentication and Core Information ---
#
# # Base model with common user attributes (non-sensitive)
# class UserBase(BaseModel):
#     email: EmailStr
#     full_name: str
#     organization_name: str
#
#
# # Model for user registration (input)
# class UserCreate(UserBase):
#     password: str
#
#
# # Model for user login (input)
# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str
#
#
# # Model representing the user structure in the MongoDB database
# # This includes sensitive information like the hashed password and expects 'id' to be the string version of _id.
# class UserInDB(UserBase):
#     id: str  # String representation of MongoDB's _id
#     hashed_password: str
#     connected_accounts: List[ConnectedAccount] = Field(default_factory=list)
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     last_login: Optional[datetime] = None
#
#     # You could add roles, preferences, subscription_status, etc. here
#
#     class Config:
#         json_encoders = {
#             datetime: lambda dt: dt.isoformat()
#         }
#
#
# # Model for sending user data to the frontend (API response)
# # Excludes sensitive information like hashed_password.
# class UserViewModel(UserBase):
#     id: str  # String representation of MongoDB's _id
#     connected_accounts: List[ConnectedAccount] = Field(default_factory=list)
#     created_at: datetime
#     last_login: Optional[datetime] = None
#
#     # Add any other non-sensitive fields you want to expose
#
#     class Config:
#         json_encoders = {
#             datetime: lambda dt: dt.isoformat()
#         }

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# --- Social Account Details ---
class SocialPlatform(str, Enum):
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"

class ConnectedAccount(BaseModel):
    platform: SocialPlatform
    account_id: str
    name: str
    email: Optional[EmailStr] = None
    profile_picture: Optional[str] = None
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: Optional[datetime] = None
    account_type: str = "personal"
    is_active: bool = True
    connected_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

# --- User Authentication and Core Information ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    organization_name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserBase):
    id: str
    hashed_password: str
    connected_accounts: List[ConnectedAccount] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class UserViewModel(UserBase):
    id: str
    connected_accounts: List[ConnectedAccount] = Field(default_factory=list)
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

# --- Password Reset Models ---
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str