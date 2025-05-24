# Backend/app/services/cleanup_temp_connections.py - CREATE THIS FILE
import asyncio
import logging
from datetime import datetime
from app.database import connected_accounts_collection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def cleanup_expired_temp_connections():
    """
    Clean up expired temporary LinkedIn connections.
    This should be run periodically to prevent database clutter.
    """
    try:
        # Delete temporary connections that have expired
        result = await connected_accounts_collection.delete_many({
            "temp": True,
            "temp_expires": {"$lt": datetime.utcnow()}
        })
        
        if result.deleted_count > 0:
            logger.info(f"Cleaned up {result.deleted_count} expired temporary LinkedIn connections")
        
        return result.deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning up temporary connections: {str(e)}")
        return 0

# Optional: You can add this to your scheduler or run it manually
if __name__ == "__main__":
    asyncio.run(cleanup_expired_temp_connections())