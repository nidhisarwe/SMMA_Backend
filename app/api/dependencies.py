# Backend/app/api/dependencies.py - IMPROVED VERSION
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# HTTP Bearer token scheme for Firebase JWT
bearer_scheme = HTTPBearer(auto_error=False)

# Check if we're in development mode
DEV_MODE = os.getenv("ENVIRONMENT", "development").lower() == "development"
if DEV_MODE:
    logger.warning("⚠️ Running in DEVELOPMENT mode - authentication may be relaxed")
else:
    logger.info("🔒 Running in PRODUCTION mode - strict authentication enforced")

async def auth_required(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)) -> str:
    """
    Validates the Firebase JWT token and returns the user ID.
    This function should be used as a dependency for all protected routes.
    Implements strict user authentication and data isolation.
    """
    logger.info("🔍 auth_required called")
    
    # Check if Firebase is properly configured
    firebase_configured = (
        os.getenv("FIREBASE_PROJECT_ID") and 
        (
            os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH") or
            os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON") or
            os.getenv("FIREBASE_PRIVATE_KEY")
        )
    )
    
    logger.debug(f"🔧 Firebase configured: {firebase_configured}")
    
    # Always accept credentials if provided, even in development mode
    if credentials:
        try:
            logger.debug("🔍 Importing Firebase admin")
            # Import here to avoid circular imports
            from app.core.firebase_admin import verify_firebase_token, get_firebase_user
            
            # Extract token from the Authorization header
            token = credentials.credentials
            if not token:
                logger.error("❌ Empty token provided")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
            logger.debug(f"🔑 Token received (length: {len(token)})")
            
            # Verify the token with revocation check in production
            # In development, we're more lenient to facilitate testing
            check_revoked = not DEV_MODE
            firebase_uid = verify_firebase_token(token, check_revoked=check_revoked)
            
            if not firebase_uid:
                logger.error("❌ Token verification failed")
                if DEV_MODE:
                    # In development mode, use a test user ID if verification fails
                    logger.warning("⚠️ Development mode: Using test user ID despite token verification failure")
                    firebase_uid = "test_user_firebase_uid_12345"
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired authentication token",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
            
            # Additional verification: ensure the user exists and is not disabled
            # In development mode, skip this check if we're using the test user ID
            if firebase_uid != "test_user_firebase_uid_12345":
                user_record = get_firebase_user(firebase_uid)
                if not user_record and not DEV_MODE:
                    logger.error(f"❌ User {firebase_uid} not found in Firebase")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User account not found or disabled",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
            elif DEV_MODE:
                logger.info(f"✅ Development mode: Using test user {firebase_uid} without Firebase validation")
                
            # Log authentication success with email if available
            if firebase_uid == "test_user_firebase_uid_12345":
                logger.info(f"✅ Authentication successful for test user: {firebase_uid}")
            else:
                user_email = getattr(user_record, 'email', 'unknown')
                logger.info(f"✅ Authentication successful for user: {firebase_uid} ({user_email})")
                
            return firebase_uid
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except ImportError as e:
            logger.error(f"❌ Firebase admin not available: {e}")
            # Fall through to development mode check below
        except Exception as e:
            # Log the error but provide a generic message to the client
            logger.error(f"❌ Authentication error: {str(e)}")
            logger.error(f"❌ Error type: {type(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"}
            )
    else:
        logger.warning("⚠️ No credentials provided")
    
    # Development mode fallback
    if DEV_MODE:
        test_user_id = "test_user_firebase_uid_12345"
        logger.warning(f"⚠️ DEVELOPMENT MODE: Using test user ID: {test_user_id}")
        return test_user_id
    
    # If we get here, authentication failed and we're not in development mode
    logger.error("❌ Authentication failed and not in development mode")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Please login to access this resource.",
        headers={"WWW-Authenticate": "Bearer"}
    )

async def optional_auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)) -> Optional[str]:
    """
    Optional authentication dependency.
    Returns the user ID if authenticated, None otherwise.
    """
    if not credentials:
        return None
    
    try:
        return await auth_required(credentials)
    except HTTPException:
        return None
    except Exception as e:
        logger.error(f"Optional authentication error: {str(e)}")
        return None


def resource_owner_required(resource_owner_id: str):
    """
    Factory function that creates a dependency to ensure the authenticated user
    is the owner of the resource being accessed.
    
    This function is crucial for proper user data isolation, ensuring users can only
    access their own resources.
    
    Args:
        resource_owner_id: The ID of the user who owns the resource
        
    Returns:
        A dependency function that validates the current user has permission to access the resource
    """
    async def validate_resource_ownership(current_user_id: str = Depends(auth_required)) -> str:
        """
        Validates that the current user is the owner of the resource.
        
        Args:
            current_user_id: The ID of the authenticated user from auth_required dependency
            
        Returns:
            The user ID if validation succeeds
            
        Raises:
            HTTPException: If the user is not the owner of the resource
        """
        # In development mode, we might want to be more lenient
        if DEV_MODE and current_user_id.startswith("test_user"):
            logger.warning(f"⚠️ DEVELOPMENT MODE: Bypassing ownership check for test user {current_user_id}")
            return current_user_id
            
        # Import here to avoid circular imports
        from app.core.firebase_admin import validate_user_resource_access
        
        # Check if the current user is the owner of the resource
        if validate_user_resource_access(current_user_id, resource_owner_id):
            return current_user_id
            
        # If we get here, the user is not the owner of the resource
        logger.warning(f"🚫 User {current_user_id} attempted to access resource owned by {resource_owner_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )
        
    return validate_resource_ownership