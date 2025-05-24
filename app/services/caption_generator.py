# Backend/app/services/caption_generator.py - FIXED
import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def enhance_prompt(prompt: str, platform: str, is_carousel: bool = False) -> str:
    """Enhanced prompt engineering for better captions"""
    
    # Base instructions for all platforms
    base_instruction = f"""Write a compelling social media caption for: "{prompt}"

Requirements:
- Write ONLY the caption content, no extra formatting or explanations
- Make it engaging and authentic
- Use a conversational tone that encourages interaction
- Include relevant emojis naturally (2-4 emojis maximum)
- End with a clear call-to-action question or statement
"""
    
    # Platform-specific enhancements
    platform_specs = {
        "instagram": f"""{base_instruction}
- Length: 150-300 words maximum
- Include 5-8 relevant hashtags at the end
- Use line breaks for readability
- Focus on visual storytelling
- Include trending hashtags when appropriate""",
        
        "twitter": f"""{base_instruction}
- Length: 240 characters maximum (leave room for interactions)
- Be concise and punchy
- Use 1-2 relevant hashtags maximum
- Create urgency or curiosity""",
        
        "linkedin": f"""{base_instruction}
- Length: 150-300 words
- Professional but engaging tone
- Focus on insights, lessons, or professional value
- Use 3-5 relevant hashtags
- Encourage professional discussion""",
        
        "facebook": f"""{base_instruction}
- Length: 100-250 words
- Conversational and relatable tone
- Encourage comments and shares
- Use 2-3 hashtags maximum""",
        
        "general": f"""{base_instruction}
- Length: 150-250 words
- Adaptable for multiple platforms
- Use 3-5 hashtags"""
    }
    
    # Add carousel-specific instructions
    if is_carousel:
        carousel_addition = "\n- This is for a carousel/multi-image post, so reference 'swipe for more' or 'see all slides'"
        platform_specs[platform] += carousel_addition
    
    return platform_specs.get(platform.lower(), platform_specs["general"])

def generate_caption(prompt: str, max_tokens: int = 300, temperature: float = 0.8, platform: str = "general", is_carousel: bool = False) -> str:
    """Generates a social media caption using Gemini AI with improved prompting"""
    
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not found in environment variables")
        return "API key not configured. Please check your environment settings."
    
    enhanced_prompt = enhance_prompt(prompt, platform, is_carousel)
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": enhanced_prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
            "topP": 0.9,
            "topK": 40,
            "stopSequences": ["**", "---", "Note:", "Caption:", "Here's"]  # Stop unwanted formatting
        }
    }

    try:
        logger.info(f"Generating caption for platform: {platform}, carousel: {is_carousel}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()

        # Extract and clean the caption
        if "candidates" in result and len(result["candidates"]) > 0:
            candidate = result["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                raw_caption = candidate["content"]["parts"][0]["text"].strip()
                
                # Clean up the caption - remove unwanted formatting
                cleaned_caption = clean_caption_response(raw_caption)
                
                logger.info(f"Successfully generated caption: {cleaned_caption[:50]}...")
                return cleaned_caption
            else:
                logger.error("Unexpected response structure - missing content/parts")
                return "Could not generate caption - invalid response structure."
        else:
            logger.error("No candidates in response")
            return "Could not generate caption - no response received."
            
    except requests.exceptions.Timeout:
        logger.error("Request timeout when calling Gemini API")
        return "Caption generation timed out. Please try again."
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return "Failed to connect to caption generation service."
    except KeyError as e:
        logger.error(f"KeyError parsing response: {str(e)}")
        return "Unexpected error in response format."
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return "An unexpected error occurred during caption generation."

def clean_caption_response(raw_caption: str) -> str:
    """Clean up the AI response to return only the caption content"""
    
    # Remove common unwanted prefixes/suffixes
    unwanted_patterns = [
        "Here's a", "Here is a", "Caption:", "**Caption:**", 
        "**", "---", "Note:", "Remember:", "Tip:",
        "This caption", "The caption", "Your caption"
    ]
    
    lines = raw_caption.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip lines that start with unwanted patterns
        skip_line = False
        for pattern in unwanted_patterns:
            if line.lower().startswith(pattern.lower()):
                skip_line = True
                break
        
        if not skip_line:
            # Remove markdown formatting
            line = line.replace('**', '').replace('*', '')
            cleaned_lines.append(line)
    
    # Join lines and clean up extra spaces
    final_caption = '\n'.join(cleaned_lines).strip()
    
    # Remove multiple consecutive newlines
    while '\n\n\n' in final_caption:
        final_caption = final_caption.replace('\n\n\n', '\n\n')
    
    return final_caption if final_caption else raw_caption.strip()