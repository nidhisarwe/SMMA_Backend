import os
import httpx
from urllib.parse import urlencode
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import HTTPException
import logging
import json

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinkedInService:
    def __init__(self):
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI")
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            logger.error("Missing LinkedIn environment variables")
            raise ValueError(
                "Missing LinkedIn environment variables: LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, or LINKEDIN_REDIRECT_URI")
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.profile_url = "https://api.linkedin.com/v2/userinfo"
        self.scopes = ["openid", "profile", "email", "w_member_social"]

    async def get_auth_url(self, state: str = None):
        try:
            if not state:
                state = "random_state_string"
            params = {
                "response_type": "code",
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "scope": " ".join(self.scopes),
                "state": state
            }
            auth_url = f"{self.auth_url}?{urlencode(params)}"
            if not auth_url.startswith("https://www.linkedin.com"):
                logger.error(f"Invalid auth URL generated: {auth_url}")
                raise ValueError("Generated LinkedIn auth URL is invalid")
            logger.info(f"Generated auth URL: {auth_url}")
            return auth_url
        except Exception as e:
            logger.error(f"Failed to generate LinkedIn auth URL: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to generate LinkedIn auth URL: {str(e)}")

    async def exchange_code_for_token(self, code: str):
        """Exchange authorization code for access token"""
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=token_data)
            if response.status_code != 200:
                logger.error(f"Failed to exchange code for token: {response.text}")
                raise HTTPException(status_code=400, detail="Failed to get access token")
            return response.json()

    async def get_user_profile(self, access_token: str):
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(self.profile_url, headers=headers)
            if response.status_code != 200:
                logger.error(f"Failed to get user profile: {response.text}")
                raise HTTPException(status_code=400, detail="Failed to get user profile")
            return response.json()

    async def refresh_token(self, refresh_token: str):
        token_data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=token_data)
            if response.status_code != 200:
                return None
            return response.json()

    async def register_image(self, access_token: str, image_url: str, author_urn: str):
        """Register a single image with LinkedIn to get a media asset URN

        Args:
            access_token (str): LinkedIn access token
            image_url (str): URL to the image to register
            author_urn (str): The URN of the author who will post the content

        Returns:
            str: The media asset URN for the registered image
        """
        register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

        # The key fix: use the author_urn as the owner
        # This resolves the "contents not owned by author" error
        register_data = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": author_urn,  # This must match the author in the post
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }

        logger.info(f"Registering LinkedIn image with owner: {author_urn}")
        logger.info(f"Image URL: {image_url}")

        try:
            # Fetch the image from the URL
            async with httpx.AsyncClient() as client:
                logger.info(f"Fetching image from URL: {image_url}")
                img_response = await client.get(image_url)
                if img_response.status_code != 200:
                    logger.error(f"Failed to fetch image from URL: {image_url}")
                    raise HTTPException(status_code=400, detail="Failed to fetch image from URL")

                # Get the image data
                image_data = img_response.content

                # Register the upload with LinkedIn
                logger.info("Registering upload with LinkedIn")
                response = await client.post(register_url, json=register_data, headers=headers)

                if response.status_code != 200:
                    logger.error(f"Failed to register image upload: {response.text}")
                    raise HTTPException(status_code=400, detail=f"Failed to register image upload: {response.text}")

                upload_info = response.json()
                upload_url = upload_info.get("value", {}).get("uploadMechanism", {}).get(
                    "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}).get("uploadUrl")
                asset_id = upload_info.get("value", {}).get("asset")

                logger.info(f"Got asset ID: {asset_id}")
                logger.info(f"Got upload URL: {upload_url}")

                if not upload_url or not asset_id:
                    logger.error("Failed to get upload URL or asset ID")
                    raise HTTPException(status_code=400, detail="Failed to get upload URL or asset ID")

                # Upload the image to the provided URL
                logger.info("Uploading image to LinkedIn")
                upload_response = await client.put(upload_url, content=image_data)

                if upload_response.status_code not in [200, 201]:
                    logger.error(f"Failed to upload image: {upload_response.text}")
                    raise HTTPException(status_code=400, detail=f"Failed to upload image: {upload_response.text}")

                logger.info(f"Successfully uploaded image to LinkedIn with asset ID: {asset_id}")
                return asset_id

        except Exception as e:
            logger.error(f"Error registering image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error registering image: {str(e)}")

    async def create_post(self, access_token: str, user_urn: str, content: str, image_url=None):
        """Create a post on LinkedIn

        Args:
            access_token (str): The access token for LinkedIn API
            user_urn (str): LinkedIn user URN (e.g., urn:li:person:abc123)
            content (str): The text content of the post
            image_url (str or list, optional): URL to an image or list of image URLs for carousel

        Returns:
            str: The post ID if successful
        """
        post_url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

        # Check if we have images to process
        if image_url:
            try:
                # Handle both single image and carousel (list of images)
                if isinstance(image_url, list):
                    # For carousel posts, we'll use only the first image for LinkedIn
                    # LinkedIn doesn't support multiple images in a single post through API
                    logger.info(f"Carousel detected with {len(image_url)} images. Using first image for LinkedIn.")
                    if len(image_url) > 0:
                        single_image_url = image_url[0]
                        logger.info(f"Selected image URL: {single_image_url}")

                        # Register and upload the first image
                        media_asset = await self.register_image(access_token, single_image_url, user_urn)
                        logger.info(f"Successfully registered image with asset ID: {media_asset}")

                        # Create a post with the image
                        post_data = {
                            "author": user_urn,
                            "lifecycleState": "PUBLISHED",
                            "specificContent": {
                                "com.linkedin.ugc.ShareContent": {
                                    "shareCommentary": {
                                        "text": content
                                    },
                                    "shareMediaCategory": "IMAGE",
                                    "media": [
                                        {
                                            "status": "READY",
                                            "description": {
                                                "text": "Image shared via SocialSync"
                                            },
                                            "media": media_asset
                                        }
                                    ]
                                }
                            },
                            "visibility": {
                                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                            }
                        }
                    else:
                        # Empty carousel, fallback to text-only
                        logger.warning("Empty carousel detected. Falling back to text-only post.")
                        post_data = {
                            "author": user_urn,
                            "lifecycleState": "PUBLISHED",
                            "specificContent": {
                                "com.linkedin.ugc.ShareContent": {
                                    "shareCommentary": {
                                        "text": content
                                    },
                                    "shareMediaCategory": "NONE"
                                }
                            },
                            "visibility": {
                                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                            }
                        }
                else:
                    # Single image case
                    logger.info(f"Registering single image for LinkedIn post: {image_url}")
                    logger.info(f"Using author URN: {user_urn}")

                    # Register the image
                    media_asset = await self.register_image(access_token, image_url, user_urn)
                    logger.info(f"Successfully registered image with asset ID: {media_asset}")

                    # Create a post with the image
                    post_data = {
                        "author": user_urn,
                        "lifecycleState": "PUBLISHED",
                        "specificContent": {
                            "com.linkedin.ugc.ShareContent": {
                                "shareCommentary": {
                                    "text": content
                                },
                                "shareMediaCategory": "IMAGE",
                                "media": [
                                    {
                                        "status": "READY",
                                        "description": {
                                            "text": "Image shared via SocialSync"
                                        },
                                        "media": media_asset
                                    }
                                ]
                            }
                        },
                        "visibility": {
                            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                        }
                    }
            except Exception as e:
                logger.error(f"Error processing image for LinkedIn post: {str(e)}")
                logger.warning("Falling back to text-only post")

                # Fallback to text-only post
                post_data = {
                    "author": user_urn,
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {
                                "text": content
                            },
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }
        else:
            # Text-only post
            post_data = {
                "author": user_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

        logger.info(f"Creating LinkedIn post with data: {json.dumps(post_data, indent=2)}")

        async with httpx.AsyncClient() as client:
            response = await client.post(post_url, json=post_data, headers=headers)
            if response.status_code != 201:
                logger.error(f"Failed to post to LinkedIn: {response.text}")
                raise HTTPException(status_code=400, detail=f"Failed to post to LinkedIn: {response.text}")

            post_id = response.headers.get("x-restli-id")
            logger.info(f"Successfully created LinkedIn post with ID: {post_id}")
            return post_id