import os
import requests
import time
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()
API_KEY = os.getenv("HF_IMAGE_API_KEY")

if not API_KEY:
    raise Exception("Hugging Face API key not configured")

# Supported models with fallback order
MODELS = [
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5",
    # "CompVis/stable-diffusion-v1-4"
]


def generate_image(prompt: str):
    """Generate image from text prompt with model fallback"""
    if not API_KEY:
        logger.error("Hugging Face API key not configured")
        raise Exception("Hugging Face API key not configured. Please set the HF_IMAGE_API_KEY environment variable.")

    if not prompt or not prompt.strip():
        logger.error("Empty prompt provided")
        raise ValueError("Prompt cannot be empty")
        
    logger.info(f"Generating image with prompt: {prompt[:50]}..." if len(prompt) > 50 else f"Generating image with prompt: {prompt}")
    headers = {"Authorization": f"Bearer {API_KEY}"}
    last_error = None

    for model in MODELS:
        try:
            logger.info(f"Trying model: {model}")
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=headers,
                json={"inputs": prompt},
                timeout=30
            )

            if response.status_code == 200:
                logger.info(f"Successfully generated image with model: {model}")
                return response.content

            # Handle specific error cases
            try:
                error_data = response.json()
            except Exception as e:
                logger.warning(f"Failed to parse error response: {e}")
                error_data = {}

            if "estimated_time" in error_data:
                wait_time = min(error_data.get("estimated_time", 10), 15)  # Cap at 15 seconds
                logger.info(f"Model {model} is loading, waiting {wait_time} seconds")
                time.sleep(wait_time)

                # Retry once after waiting
                logger.info(f"Retrying model {model} after waiting")
                response = requests.post(
                    f"https://api-inference.huggingface.co/models/{model}",
                    headers=headers,
                    json={"inputs": prompt},
                    timeout=30
                )

                if response.status_code == 200:
                    logger.info(f"Successfully generated image with model {model} after waiting")
                    return response.content
                else:
                    last_error = error_data.get("error", "Model is still loading")
                    logger.warning(f"Model {model} still failed after waiting: {last_error}")

            elif "error" in error_data:
                last_error = error_data["error"]
                logger.warning(f"Error from model {model}: {last_error}")
            else:
                last_error = f"API returned status code {response.status_code}"
                logger.warning(f"Unexpected status code from model {model}: {response.status_code}")

        except requests.exceptions.RequestException as e:
            last_error = str(e)
            logger.warning(f"Request exception with model {model}: {last_error}")
            continue  # Try next model

    error_msg = last_error or "All models failed to generate image"
    logger.error(f"Image generation failed: {error_msg}")
    raise Exception(error_msg)