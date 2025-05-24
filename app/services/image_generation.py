import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("HF_IMAGE_API_KEY")

# Supported models with fallback order
MODELS = [
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5",
    # "CompVis/stable-diffusion-v1-4"
]


def generate_image(prompt: str):
    """Generate image from text prompt with model fallback"""
    if not API_KEY:
        raise Exception("Hugging Face API key not configured")

    headers = {"Authorization": f"Bearer {API_KEY}"}

    last_error = None

    for model in MODELS:
        try:
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=headers,
                json={"inputs": prompt},
                timeout=30
            )

            if response.status_code == 200:
                return response.content

            # Handle specific error cases
            error_data = response.json()

            if "estimated_time" in error_data:
                wait_time = error_data.get("estimated_time", 10)
                time.sleep(wait_time)

                # Retry once after waiting
                response = requests.post(
                    f"https://api-inference.huggingface.co/models/{model}",
                    headers=headers,
                    json={"inputs": prompt},
                    timeout=30
                )

                if response.status_code == 200:
                    return response.content
                else:
                    last_error = error_data.get("error", "Model is still loading")

            elif "error" in error_data:
                last_error = error_data["error"]
            else:
                last_error = f"API returned status code {response.status_code}"

        except requests.exceptions.RequestException as e:
            last_error = str(e)
            continue  # Try next model

    raise Exception(last_error or "All models failed to generate image")