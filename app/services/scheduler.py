import asyncio
import logging
import datetime
import pytz
from typing import Dict, Any
import httpx
from app.database import scheduled_posts_collection, connected_accounts_collection
from app.models.user import SocialPlatform
from bson import ObjectId

logger = logging.getLogger(__name__)

# Define the timezone for IST
IST = pytz.timezone('Asia/Kolkata')


class PostScheduler:
    """Service for scheduling and executing social media posts at specific times using IST timezone"""

    def __init__(self):
        self.scheduled_tasks = {}
        self.is_running = False

    async def start(self):
        """Start the scheduler service"""
        if self.is_running:
            return

        self.is_running = True
        logger.info("Starting post scheduler service")
        asyncio.create_task(self._scheduler_loop())

    async def stop(self):
        """Stop the scheduler service"""
        self.is_running = False
        logger.info("Stopping post scheduler service")
        for task in self.scheduled_tasks.values():
            task.cancel()

    async def _scheduler_loop(self):
        """Main scheduler loop that checks for posts to publish every minute"""
        while self.is_running:
            try:
                await self._check_posts_to_publish()
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")

            # Wait for 1 minute before checking again
            await asyncio.sleep(60)

    async def _check_posts_to_publish(self):
        """Check for posts that are scheduled to be published in the next 5 minutes"""
        # Get current time in UTC
        now_utc = datetime.datetime.utcnow()
        window_end_utc = now_utc + datetime.timedelta(minutes=5)

        # Log times in both UTC and IST for debugging
        now_ist = now_utc.replace(tzinfo=pytz.UTC).astimezone(IST)
        window_end_ist = window_end_utc.replace(tzinfo=pytz.UTC).astimezone(IST)

        logger.info(f"Checking for posts to publish between {now_utc} and {window_end_utc} UTC")
        logger.info(f"Current time in IST: {now_ist.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")
        logger.info(f"Window end in IST: {window_end_ist.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")

        # DEBUG: Log all scheduled posts for troubleshooting
        async for post in scheduled_posts_collection.find({"status": "scheduled"}):
            post_id = str(post["_id"])
            scheduled_time = post["scheduled_time"]
            scheduled_time_ist = scheduled_time.replace(tzinfo=pytz.UTC).astimezone(IST)
            logger.info(
                f"Found scheduled post {post_id} set for {scheduled_time} UTC / {scheduled_time_ist.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")

        # Query for posts scheduled to publish in the next 5 minutes (stored in UTC)
        # IMPORTANT: Make sure we're retrieving posts properly by using exact field names and types
        upcoming_posts = scheduled_posts_collection.find({
            "scheduled_time": {"$gte": now_utc, "$lte": window_end_utc},
            "status": "scheduled"
        })

        post_count = 0
        async for post in upcoming_posts:
            post_count += 1
            post_id = str(post["_id"])

            # If we already have a task for this post, skip it
            if post_id in self.scheduled_tasks:
                logger.info(f"Post {post_id} already has a scheduled task, skipping")
                continue

            # Get scheduled time (stored in UTC) and log it in both UTC and IST for debugging
            publish_time_utc = post["scheduled_time"]
            publish_time_ist = publish_time_utc.replace(tzinfo=pytz.UTC).astimezone(IST)

            logger.info(
                f"Found post {post_id} to publish at {publish_time_utc} UTC / {publish_time_ist.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")

            # Calculate seconds until publish time
            seconds_until_publish = (publish_time_utc - now_utc).total_seconds()

            if seconds_until_publish < 0:
                # If the post is already past its scheduled time, publish immediately
                logger.warning(f"Post {post_id} is past its scheduled time, publishing immediately")
                seconds_until_publish = 0

            # Schedule the publish task
            task = asyncio.create_task(self._schedule_publish(post, seconds_until_publish))
            self.scheduled_tasks[post_id] = task

            # Set up task cleanup when it completes
            task.add_done_callback(lambda _: self.scheduled_tasks.pop(post_id, None))

        logger.info(f"Found {post_count} post(s) to schedule for publishing")

    async def _schedule_publish(self, post: Dict[str, Any], delay_seconds: float):
        """Schedule a post to be published after the specified delay"""
        post_id = str(post["_id"])
        logger.info(f"Scheduling post {post_id} to publish in {delay_seconds:.1f} seconds")

        try:
            # Wait until it's time to publish
            await asyncio.sleep(delay_seconds)

            # Publish the post
            await self._publish_post(post)

            # Update the post status
            await scheduled_posts_collection.update_one(
                {"_id": ObjectId(post_id)},
                {"$set": {"status": "published", "published_at": datetime.datetime.utcnow()}}
            )

            logger.info(f"Successfully published post {post_id}")

        except asyncio.CancelledError:
            logger.info(f"Publishing task for post {post_id} was cancelled")

        except Exception as e:
            logger.error(f"Failed to publish post {post_id}: {str(e)}")

            # Update the post status to failed
            await scheduled_posts_collection.update_one(
                {"_id": ObjectId(post_id)},
                {
                    "$set": {
                        "status": "failed",
                        "error": str(e),
                        "attempted_at": datetime.datetime.utcnow()
                    }
                }
            )

    async def _publish_post(self, post: Dict[str, Any]):
        """Publish a post to the specified platform"""
        platform = post.get("platform", "").lower()
        user_id = post.get("user_id", "current_user_id")

        logger.info(f"Publishing post to {platform} for user {user_id}")

        if platform == "linkedin":
            await self._publish_to_linkedin(post, user_id)
        elif platform == "facebook":
            # Implement Facebook publishing
            raise NotImplementedError("Facebook publishing not implemented yet")
        elif platform == "twitter":
            # Implement Twitter publishing
            raise NotImplementedError("Twitter publishing not implemented yet")
        elif platform == "instagram":
            # Implement Instagram publishing
            raise NotImplementedError("Instagram publishing not implemented yet")
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    async def _publish_to_linkedin(self, post: Dict[str, Any], user_id: str):
        """Publish a post to LinkedIn"""
        # Find the LinkedIn account for this user
        logger.info(f"Looking for active LinkedIn account for user {user_id}")
        account = await connected_accounts_collection.find_one({
            "user_id": user_id,
            "platform": SocialPlatform.LINKEDIN.value,
            "is_active": True
        })

        if not account:
            logger.error(f"No connected LinkedIn account found for user {user_id}")
            raise ValueError(f"No connected LinkedIn account found for user {user_id}")

        logger.info(f"Found LinkedIn account: {account.get('name')} (ID: {account.get('account_id_on_platform')})")

        # Call the LinkedIn post endpoint with the post data
        try:
            async with httpx.AsyncClient() as client:
                logger.info(f"Sending post request to LinkedIn API")
                response = await client.post(
                    "http://127.0.0.1:8000/api/post-now/",
                    json={
                        "platform": "linkedin",
                        "caption": post["caption"],
                        "image_url": post["image_url"],
                        "is_carousel": post.get("is_carousel", False),
                        "user_id": user_id
                    },
                    timeout=3600  # 60 second timeout for image processing
                )

                if response.status_code != 200:
                    error_detail = response.json().get("detail", "Unknown error")
                    logger.error(f"LinkedIn posting failed with status {response.status_code}: {error_detail}")
                    raise ValueError(f"LinkedIn posting failed: {error_detail}")

                result = response.json()
                logger.info(f"LinkedIn post successful: {result}")
                return result

        except httpx.TimeoutException:
            logger.error(f"Timeout when publishing to LinkedIn")
            raise ValueError("Timeout when publishing to LinkedIn")
        except Exception as e:
            logger.error(f"Exception when publishing to LinkedIn: {str(e)}")
            raise


# Create a global instance of the scheduler
scheduler = PostScheduler()


# Function to start the scheduler at application startup
async def start_scheduler():
    logger.info("Starting post scheduler at application startup")
    await scheduler.start()


# Function to stop the scheduler at application shutdown
async def stop_scheduler():
    logger.info("Stopping post scheduler at application shutdown")
    await scheduler.stop()
