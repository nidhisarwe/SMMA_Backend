# backend/app/core/security.py
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .firebase_admin import verify_firebase_token
from typing import Optional

# Use bcrypt for password hashing (for legacy support)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme for Firebase JWT
bearer_scheme = HTTPBearer(auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)

async def get_current_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)) -> str:
    """
    Validates the Firebase JWT token and returns the user ID.
    This function can be used as a FastAPI dependency.
    
    Args:
        credentials: The HTTP Authorization header containing the Bearer token
        
    Returns:
        The user ID from the token
        
    Raises:
        HTTPException: If the token is missing or invalid
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials not provided",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Extract token from the Authorization header
        token = credentials.credentials
        
        # Verify the token and get the user ID
        user_id = verify_firebase_token(token)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token. Please login again.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user_id
    except Exception as e:
        # Log the error but provide a generic message to the client
        print(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. Please login again.",
            headers={"WWW-Authenticate": "Bearer"}
        )