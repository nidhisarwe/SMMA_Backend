from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
import re
from enum import Enum


class SocialPlatform(str, Enum):
    """Enum for social media platforms"""
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    TIKTOK = "tiktok"


class UserCreate(BaseModel):
    """Model for user registration"""
    email: EmailStr
    password: str
    full_name: str
    organization_name: Optional[str] = None
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v


class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr
    password: str


class UserViewModel(BaseModel):
    """Model for user data returned to frontend"""
    id: str
    email: EmailStr
    full_name: str
    organization_name: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    connected_accounts: Optional[List[Dict[str, Any]]] = []


class PasswordResetRequest(BaseModel):
    """Model for password reset request"""
    email: EmailStr


class PasswordReset(BaseModel):
    """Model for password reset"""
    token: str
    new_password: str
    
    @validator('new_password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v


class FirebaseAuth(BaseModel):
    """Model for Firebase authentication"""
    token: str


class UserProfile(BaseModel):
    """Model for user profile updates"""
    full_name: Optional[str] = None
    organization_name: Optional[str] = None
    connected_accounts: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        extra = "ignore"  # Ignore extra fields
