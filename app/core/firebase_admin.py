# Backend/app/core/firebase_admin.py - FIXED VERSION
import os
import json
from typing import Optional
import logging
import pathlib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import firebase_admin
    from firebase_admin import credentials, auth
    FIREBASE_AVAILABLE = True
    logger.info("✅ Firebase Admin SDK imported successfully")
except ImportError as e:
    logger.warning(f"❌ Firebase Admin SDK not available: {e}")
    logger.warning("Please install firebase-admin package: pip install firebase-admin")
    FIREBASE_AVAILABLE = False
    firebase_admin = None
    auth = None

def initialize_firebase() -> bool:
    """
    Initialize Firebase Admin SDK with proper error handling.
    Returns True if successful, False otherwise.
    """
    if not FIREBASE_AVAILABLE:
        logger.warning("Firebase Admin SDK not available")
        return False
    
    # Check if already initialized
    if len(firebase_admin._apps) > 0:
        logger.info("✅ Firebase already initialized")
        return True
    
    try:
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        if not project_id:
            logger.error("❌ FIREBASE_PROJECT_ID not found in environment variables")
            return False
        
        # Try service account file first
        service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        if service_account_path:
            # Handle relative paths
            if service_account_path.startswith("./") or service_account_path.startswith("../"):
                # Convert relative path to absolute path
                base_dir = pathlib.Path(os.getcwd())
                service_account_path = str(base_dir / service_account_path.lstrip("./"))
                logger.info(f"Converted relative path to absolute path: {service_account_path}")
            
            if os.path.exists(service_account_path):
                logger.info(f"🔑 Using service account file: {service_account_path}")
                try:
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred, {
                        'projectId': project_id
                    })
                    logger.info("✅ Firebase initialized with service account file")
                    return True
                except Exception as e:
                    logger.error(f"❌ Error loading service account file: {e}")
            else:
                logger.error(f"❌ Service account file not found at path: {service_account_path}")
        
        # Try service account JSON from environment variable
        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if service_account_json:
            logger.info("🔑 Using service account JSON from environment variable")
            try:
                service_account_info = json.loads(service_account_json)
                cred = credentials.Certificate(service_account_info)
                firebase_admin.initialize_app(cred, {
                    'projectId': project_id
                })
                logger.info("✅ Firebase initialized with service account JSON")
                return True
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON in FIREBASE_SERVICE_ACCOUNT_JSON: {e}")
        
        # Try individual environment variables
        private_key = os.getenv("FIREBASE_PRIVATE_KEY")
        client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
        
        if private_key and client_email:
            logger.info("🔑 Using individual Firebase environment variables")
            
            # Replace escaped newlines
            private_key = private_key.replace('\\n', '\n')
            
            service_account_info = {
                "type": "service_account",
                "project_id": project_id,
                "private_key": private_key,
                "client_email": client_email,
                "client_id": os.getenv("FIREBASE_CLIENT_ID", ""),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email}"
            }
            
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred, {
                'projectId': project_id
            })
            logger.info("✅ Firebase initialized with individual environment variables")
            return True
        
        # Try Application Default Credentials (for production environments)
        logger.info("🔑 Trying Application Default Credentials")
        try:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'projectId': project_id
            })
            logger.info("✅ Firebase initialized with Application Default Credentials")
            return True
        except Exception as adc_error:
            logger.error(f"❌ Failed to initialize with Application Default Credentials: {adc_error}")
        
        # If we get here, all initialization methods failed
        logger.error("❌ All Firebase initialization methods failed")
        return False
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Firebase: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        return False

def verify_firebase_token(token: str, check_revoked: bool = True) -> Optional[str]:
    """
    Verify Firebase ID token and return the user ID.
    
    Args:
        token: The Firebase ID token to verify
        check_revoked: Whether to check if the token has been revoked
        
    Returns:
        The user ID if the token is valid, None otherwise
    """
    # Check if we're in development mode
    DEV_MODE = os.getenv("ENVIRONMENT", "development").lower() == "development"
    
    if not FIREBASE_AVAILABLE:
        logger.warning("⚠️ Firebase not available, cannot verify token")
        if DEV_MODE:
            logger.warning("⚠️ Development mode: Returning test user ID")
            return "test_user_firebase_uid_12345"
        return None
    
    if not initialize_firebase():
        logger.error("❌ Firebase not initialized, cannot verify token")
        if DEV_MODE:
            logger.warning("⚠️ Development mode: Returning test user ID despite initialization failure")
            return "test_user_firebase_uid_12345"
        return None
    
    try:
        # In development mode, be more lenient with token verification
        if DEV_MODE:
            try:
                # Try to verify the token but with reduced checks
                decoded_token = auth.verify_id_token(token, check_revoked=False)
                user_id = decoded_token.get('uid')
                if user_id:
                    logger.info(f"✅ Development mode: Token verified for user: {user_id}")
                    return user_id
            except Exception as dev_error:
                # In development mode, if token verification fails, log it but continue with test user
                logger.warning(f"⚠️ Development mode: Token verification failed, using test user: {str(dev_error)}")
                return "test_user_firebase_uid_12345"
        
        # Production mode - strict verification
        # Verify the token with additional security checks
        decoded_token = auth.verify_id_token(token, check_revoked=check_revoked)
        
        # Check token expiration
        exp = decoded_token.get('exp')
        if not exp:
            logger.error("❌ Token has no expiration time")
            return None
            
        # Get user ID from token
        user_id = decoded_token.get('uid')
        if not user_id:
            logger.error("❌ No user ID found in token")
            return None
            
        # Check if user exists and is not disabled
        try:
            user_record = auth.get_user(user_id)
            if user_record.disabled:
                logger.error(f"❌ User {user_id} is disabled")
                return None
        except auth.UserNotFoundError:
            logger.error(f"❌ User {user_id} not found")
            return None
        except Exception as user_error:
            logger.error(f"❌ Error checking user status: {str(user_error)}")
            # Continue with token validation if we can't check user status
            
        logger.info(f"✅ Token verified successfully for user: {user_id}")
        return user_id
            
    except auth.ExpiredIdTokenError:
        logger.error("❌ Token has expired")
        return None
    except auth.RevokedIdTokenError:
        logger.error("❌ Token has been revoked")
        return None
    except auth.InvalidIdTokenError:
        logger.error("❌ Token is invalid")
        return None
    except Exception as e:
        logger.error(f"❌ Token verification failed: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        return None

def get_firebase_user(uid: str):
    """
    Get Firebase user information by UID.
    
    Args:
        uid: The Firebase user ID
        
    Returns:
        Firebase user record if found, None otherwise
    """
    if not FIREBASE_AVAILABLE:
        logger.warning("⚠️ Firebase not available, cannot get user")
        return None
    
    if not initialize_firebase():
        logger.error("❌ Firebase not initialized, cannot get user")
        return None
    
    try:
        user_record = auth.get_user(uid)
        logger.info(f"✅ Firebase user retrieved: {user_record.email}")
        return user_record
    except auth.UserNotFoundError:
        logger.error(f"❌ Firebase user not found: {uid}")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to get Firebase user {uid}: {str(e)}")
        return None


def validate_user_resource_access(user_id: str, resource_owner_id: str) -> bool:
    """
    Validate that a user has permission to access a resource.
    This ensures proper user data isolation by verifying the user owns the resource.
    
    Args:
        user_id: The ID of the user making the request
        resource_owner_id: The ID of the user who owns the resource
        
    Returns:
        True if the user has permission, False otherwise
    """
    if not user_id or not resource_owner_id:
        logger.error(f"❌ Missing user_id or resource_owner_id in permission check")
        return False
        
    # Check if the user is the owner of the resource
    if user_id == resource_owner_id:
        logger.info(f"✅ User {user_id} has permission to access resource owned by {resource_owner_id}")
        return True
        
    # If we implement admin roles in the future, we could check for admin permissions here
    # For now, strict user isolation means only the owner can access their resources
    logger.warning(f"⚠️ User {user_id} attempted to access resource owned by {resource_owner_id}")
    return False


def create_firebase_user(email: str, password: str, display_name: str = None):
    """
    Create a new Firebase user.
    
    Args:
        email: User email
        password: User password
        display_name: Optional display name
        
    Returns:
        Firebase user record if created successfully, None otherwise
    """
    if not FIREBASE_AVAILABLE:
        logger.warning("⚠️ Firebase not available, cannot create user")
        return None
    
    if not initialize_firebase():
        logger.error("❌ Firebase not initialized, cannot create user")
        return None
    
    try:
        user_properties = {
            'email': email,
            'password': password,
            'email_verified': False,
        }
        
        if display_name:
            user_properties['display_name'] = display_name
            
        user_record = auth.create_user(**user_properties)
        logger.info(f"✅ Firebase user created: {user_record.uid}")
        return user_record
    except auth.EmailAlreadyExistsError:
        logger.error(f"❌ Email already exists: {email}")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to create Firebase user: {str(e)}")
        return None

# Initialize Firebase when the module is imported
logger.info("🚀 Initializing Firebase Admin SDK...")
firebase_initialized = initialize_firebase()

if firebase_initialized:
    logger.info("✅ Firebase Admin SDK initialized successfully")
else:
    logger.warning("⚠️ Firebase Admin SDK initialization failed - running in development mode")