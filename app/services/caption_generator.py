import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def enhance_prompt(prompt: str, platform: str) -> str:
    """Enhances user prompt based on the target platform."""
    platform_prompts = {
        "instagram": f"Create an engaging Instagram caption for: {prompt}. Use relevant hashtags and emojis.",
        "twitter": f"Write a concise, engaging tweet about: {prompt}. Stay within 280 characters.",
        "linkedin": f"Draft a professional LinkedIn post about: {prompt}.",
        "facebook": f"Create an engaging Facebook post about: {prompt}.",
        "tiktok": f"Write a catchy TikTok caption for: {prompt}.",
        "general": f"Generate an engaging social media caption for: {prompt}."
    }
    return platform_prompts.get(platform.lower(), platform_prompts["general"])

def generate_caption(prompt: str, max_tokens: int = 150, temperature: float = 0.8, platform: str = "general") -> str:
    """Generates a social media caption using Gemini AI."""
    enhanced_prompt = enhance_prompt(prompt, platform)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": enhanced_prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature, "topP": 0.9, "topK": 40}
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()

        # ✅ Fix: Extract the correct text response
        if "candidates" in result and len(result["candidates"]) > 0:
            caption_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            return caption_text
        else:
            return "Could not generate a caption at this time."
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return "Failed to generate a caption."
    except KeyError:
        logger.error("Unexpected response structure from Gemini API.")
        return "Unexpected error in response."
