import requests
import os
import logging


def post_to_instagram(image_url, caption, access_token):
    """
    Posts an image with a caption to Instagram.
    """
    if not access_token:
        return {"error": "Missing Access Token"}

    url = f"https://graph.facebook.com/v18.0/{os.getenv('INSTAGRAM_ACCOUNT_ID')}/media"
    params = {
        "image_url": image_url,
        "caption": caption,
        "access_token": access_token,
    }

    logging.info(f"📡 Sending request to Instagram: {params}")  # 🔍 Log full request details

    response = requests.post(url, params=params)
    response_data = response.json()

    logging.info(f"📡 Instagram API Response: {response_data}")  # ✅ Log Instagram API Response

    if "error" in response_data:
        logging.error(f"⚠️ Instagram Upload Error: {response_data}")  # Log error response
        return {"error": response_data["error"]["message"]}

    media_id = response_data.get("id")
    if not media_id:
        return {"error": "Failed to upload media"}

    # Publish the media
    publish_url = f"https://graph.facebook.com/v18.0/{os.getenv('INSTAGRAM_ACCOUNT_ID')}/media_publish"
    publish_params = {
        "creation_id": media_id,
        "access_token": access_token,
    }

    logging.info(f"📡 Publishing Media: {publish_params}")  # 🔍 Log publish request

    publish_response = requests.post(publish_url, params=publish_params)
    publish_data = publish_response.json()

    logging.info(f"📡 Instagram Publish Response: {publish_data}")  # ✅ Log Publish API Response

    if "error" in publish_data:
        logging.error(f"⚠️ Instagram Publish Error: {publish_data}")  # Log error response
        return {"error": publish_data["error"]["message"]}

    return publish_data
