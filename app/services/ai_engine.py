# import os
# import requests
# from dotenv import load_dotenv
#
# # Load API key from .env
# load_dotenv()
# API_KEY = os.getenv("HUGGINGFACE_API_KEY")
# API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
# HEADERS = {"Authorization": f"Bearer {API_KEY}"}
#
# def generate_response(user_query: str):
#     """Send query to Hugging Face API and return structured response."""
#     try:
#         payload = {"inputs": user_query, "parameters": {"max_new_tokens": 150, "temperature": 0.7}}
#         response = requests.post(API_URL, headers=HEADERS, json=payload)
#
#         if response.status_code == 200:
#             data = response.json()
#             generated_text = data[0]["generated_text"] if data else "Sorry, I couldn't generate a response."
#
#             # Clean response
#             response_lines = generated_text.strip().split("\n")
#             cleaned_lines = [line.strip() for line in response_lines if user_query.lower() not in line.lower()]
#
#             return "\n\n".join(cleaned_lines)  # Properly formatted response
#         else:
#             return f"API Error {response.status_code} - {response.text}"
#     except Exception as e:
#         return str(e)


# C:\Users\ABHISHEK\SocialSync\backend\app\services\ai_engine.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Verify in .env
API_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

def generate_response(user_query: str):
    try:
        payload = {
            "model": "llama3-70b-8192",  # ✅ New recommended model (June 2024)
            "messages": [
                {"role": "system", "content": "You are a helpful marketing assistant."},
                {"role": "user", "content": user_query}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()  # Crash if API fails
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {str(e)}"