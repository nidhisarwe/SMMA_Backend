# Backend/app/core/config.py - CREATE OR UPDATE THIS FILE
import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    
    # Get the path to the .env file (should be in the project root)
    env_path = Path(__file__).parent.parent.parent / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment variables from: {env_path}")
    else:
        print(f"⚠️ .env file not found at: {env_path}")
        # Try loading from current directory
        load_dotenv()
        print("✅ Attempted to load .env from current directory")
        
except ImportError:
    print("❌ python-dotenv not installed. Install with: pip install python-dotenv")
    print("⚠️ Environment variables will only be loaded from system environment")

# Configuration settings
class Settings:
    # Database
    MONGO_URI: str = os.getenv("MONGO_URI", "")
    
    # API Keys
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    HF_IMAGE_API_KEY: str = os.getenv("HF_IMAGE_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Social Media
    INSTAGRAM_ACCESS_TOKEN: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    INSTAGRAM_ACCOUNT_ID: str = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
    
    # LinkedIn
    LINKEDIN_CLIENT_ID: str = os.getenv("LINKEDIN_CLIENT_ID", "")
    LINKEDIN_CLIENT_SECRET: str = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    LINKEDIN_REDIRECT_URI: str = os.getenv("LINKEDIN_REDIRECT_URI", "")
    FRONTEND_REDIRECT_URI: str = os.getenv("FRONTEND_REDIRECT_URI", "")
    
    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    
    # Firebase
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_SERVICE_ACCOUNT_PATH: str = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "")
    FIREBASE_SERVICE_ACCOUNT_JSON: str = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "")
    FIREBASE_CLIENT_EMAIL: str = os.getenv("FIREBASE_CLIENT_EMAIL", "")
    FIREBASE_PRIVATE_KEY: str = os.getenv("FIREBASE_PRIVATE_KEY", "")
    
    def __init__(self):
        # Debug: Print Firebase config
        print("🔧 Firebase Configuration:")
        print(f"  FIREBASE_PROJECT_ID: {self.FIREBASE_PROJECT_ID}")
        print(f"  FIREBASE_SERVICE_ACCOUNT_PATH: {self.FIREBASE_SERVICE_ACCOUNT_PATH}")
        print(f"  FIREBASE_CLIENT_EMAIL: {self.FIREBASE_CLIENT_EMAIL}")
        print(f"  FIREBASE_PRIVATE_KEY: {'SET' if self.FIREBASE_PRIVATE_KEY else 'NOT SET'}")

# Create settings instance
settings = Settings()