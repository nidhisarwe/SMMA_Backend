# import os
# import httpx
# from urllib.parse import urlencode
# from dotenv import load_dotenv
# from fastapi import HTTPException
# import logging
# import uuid
#
# load_dotenv()
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# class LinkedInService:
#     def __init__(self):
#         self.client_id = os.getenv("LINKEDIN_CLIENT_ID")
#         self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
#         self.redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI")
#         if not all([self.client_id, self.client_secret, self.redirect_uri]):
#             missing_vars = [var for var in ["LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET", "LINKEDIN_REDIRECT_URI"] if not os.getenv(var)]
#             logger.error(f"Missing environment variables: {missing_vars}")
#             raise ValueError(f"Missing environment variables: {missing_vars}")
#         logger.info("LinkedInService initialized successfully")
#         self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
#         self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
#         self.profile_url = "https://api.linkedin.com/v2/userinfo"
#         self.scopes = ["openid", "profile", "email", "w_member_social"]
#
#     async def get_auth_url(self, state: str = None):
#         try:
#             if not state:
#                 state = str(uuid.uuid4())
#             logger.info(f"Generating auth URL with state: {state}")
#             params = {
#                 "response_type": "code",
#                 "client_id": self.client_id,
#                 "redirect_uri": self.redirect_uri,
#                 "scope": " ".join(self.scopes),
#                 "state": state
#             }
#             auth_url = f"{self.auth_url}?{urlencode(params)}"
#             if not auth_url.startswith("https://www.linkedin.com"):
#                 logger.error(f"Invalid auth URL generated: {auth_url}")
#                 raise ValueError("Generated LinkedIn auth URL is invalid")
#             logger.info(f"Generated auth URL: {auth_url}")
#             return auth_url
#         except Exception as e:
#             logger.error(f"Failed to generate LinkedIn auth URL: {str(e)}")
#             raise HTTPException(status_code=500, detail=f"Failed to generate LinkedIn auth URL: {str(e)}")
#
#     async def exchange_code_for_token(self, code: str):
#         token_data = {
#             "grant_type": "authorization_code",
#             "code": code,
#             "redirect_uri": self.redirect_uri,
#             "client_id": self.client_id,
#             "client_secret": self.client_secret
#         }
#         async with httpx.AsyncClient() as client:
#             response = await client.post(self.token_url, data=token_data)
#             if response.status_code != 200:
#                 logger.error(f"Token exchange failed: {response.text}")
#                 raise HTTPException(status_code=400, detail="Failed to get access token")
#             return response.json()
#
#     async def get_user_profile(self, access_token: str):
#         headers = {"Authorization": f"Bearer {access_token}"}
#         async with httpx.AsyncClient() as client:
#             response = await client.get(self.profile_url, headers=headers)
#             if response.status_code != 200:
#                 logger.error(f"Profile fetch failed: {response.text}")
#                 raise HTTPException(status_code=400, detail="Failed to get user profile")
#             return response.json()
#
#     async def refresh_token(self, refresh_token: str):
#         token_data = {
#             "grant_type": "refresh_token",
#             "refresh_token": refresh_token,
#             "client_id": self.client_id,
#             "client_secret": self.client_secret
#         }
#         async with httpx.AsyncClient() as client:
#             response = await client.post(self.token_url, data=token_data)
#             if response.status_code != 200:
#                 logger.error(f"Token refresh failed: {response.text}")
#                 return None
#             return response.json()
#
#     async def create_post(self, access_token: str, user_urn: str, content: str):
#         post_url = "https://api.linkedin.com/v2/ugcPosts"
#         headers = {
#             "Authorization": f"Bearer {access_token}",
#             "X-Restli-Protocol-Version": "2.0.0",
#             "Content-Type": "application/json"
#         }
#         post_data = {
#             "author": user_urn,
#             "lifecycleState": "PUBLISHED",
#             "specificContent": {
#                 "com.linkedin.ugc.ShareContent": {
#                     "shareCommentary": {
#                         "text": content
#                     },
#                     "shareMediaCategory": "NONE"
#                 }
#             },
#             "visibility": {
#                 "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
#             }
#         }
#         async with httpx.AsyncClient() as client:
#             response = await client.post(post_url, json=post_data, headers=headers)
#             if response.status_code != 201:
#                 logger.error(f"Post creation failed: {response.text}")
#                 raise HTTPException(status_code=400, detail="Failed to post to LinkedIn")
#             return response.headers.get("x-restli-id")


import os
import httpx
from urllib.parse import urlencode
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import HTTPException
import logging

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

    async def create_post(self, access_token: str, user_urn: str, content: str, image_url: str = None):
        """Create a post on LinkedIn

        Args:
            access_token (str): The access token for LinkedIn API
            user_urn (str): LinkedIn user URN (e.g., urn:li:person:abc123)
            content (str): The text content of the post
            image_url (str, optional): URL to an image to include in the post

        Returns:
            str: The post ID if successful
        """
        post_url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

        # Set up the post data with or without image
        if image_url:
            # Post with image requires a different payload structure
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
                                "originalUrl": image_url,
                                "media": "urn:li:digitalmediaAsset:mediaid"  # This would normally be a real ID
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            # For a real implementation, we'd first upload the image and get the media URN
            # This simplified version just posts text for demo purposes
            logger.warning("Image URL provided but image upload not implemented. Posting text only.")

            # Fallback to text-only post for now
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

        async with httpx.AsyncClient() as client:
            response = await client.post(post_url, json=post_data, headers=headers)
            if response.status_code != 201:
                logger.error(f"Failed to post to LinkedIn: {response.text}")
                raise HTTPException(status_code=400, detail=f"Failed to post to LinkedIn: {response.text}")
            return response.headers.get("x-restli-id")