# Backend/check_firebase_setup.py - CREATE THIS FILE TO DEBUG
import os
import json
from pathlib import Path

def check_firebase_setup():
    """Debug Firebase configuration"""
    print("🔍 Checking Firebase Setup...")
    print("=" * 50)
    
    # Check environment variables
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    private_key = os.getenv("FIREBASE_PRIVATE_KEY")
    client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
    
    print(f"✅ FIREBASE_PROJECT_ID: {project_id}")
    print(f"✅ FIREBASE_SERVICE_ACCOUNT_PATH: {service_account_path}")
    print(f"✅ FIREBASE_SERVICE_ACCOUNT_JSON: {'SET' if service_account_json else 'NOT SET'}")
    print(f"✅ FIREBASE_PRIVATE_KEY: {'SET' if private_key else 'NOT SET'}")
    print(f"✅ FIREBASE_CLIENT_EMAIL: {client_email}")
    
    print("\n🔍 Checking Service Account File...")
    print("=" * 50)
    
    if service_account_path:
        file_path = Path(service_account_path)
        print(f"Service account path: {file_path}")
        print(f"File exists: {file_path.exists()}")
        
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                print(f"✅ File is valid JSON")
                print(f"✅ Project ID in file: {data.get('project_id')}")
                print(f"✅ Client email in file: {data.get('client_email')}")
                print(f"✅ Private key exists: {'private_key' in data}")
            except Exception as e:
                print(f"❌ Error reading service account file: {e}")
        else:
            print(f"❌ Service account file does not exist")
    else:
        print("❌ No service account path specified")
    
    print("\n🔍 Testing Firebase Admin Import...")
    print("=" * 50)
    
    try:
        import firebase_admin
        from firebase_admin import credentials, auth
        print("✅ Firebase Admin SDK imported successfully")
        
        # Check if already initialized
        if len(firebase_admin._apps) > 0:
            print("✅ Firebase app already initialized")
        else:
            print("⚠️  Firebase app not initialized")
            
    except ImportError as e:
        print(f"❌ Firebase Admin SDK import failed: {e}")
        print("💡 Run: pip install firebase-admin")
    
    print("\n🔍 Testing Token Verification Setup...")
    print("=" * 50)
    
    try:
        from app.core.firebase_admin import verify_firebase_token, initialize_firebase
        
        # Test initialization
        init_result = initialize_firebase()
        print(f"Firebase initialization result: {init_result}")
        
        if init_result:
            print("✅ Firebase Admin SDK initialized successfully")
        else:
            print("❌ Firebase Admin SDK initialization failed")
            
    except Exception as e:
        print(f"❌ Error testing Firebase setup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_firebase_setup()