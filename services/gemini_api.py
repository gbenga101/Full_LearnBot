""" import requests
from config import Config

def simplify_text(text, level):
    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent'
    prompt = f"Simplify this text for a {level}: {text}"
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(f"{url}?key={Config.GEMINI_API_KEY}", json=data)
    if response.status_code == 200:
        try:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError, TypeError):
            return "Error: Unexpected response format"
    return f"Error: {response.status_code}"

 """
import requests
from config import Config
import json # Import the json library for more robust error parsing

def simplify_text(text, level):
    """
    Simplifies a given text using the Gemini API.

    Args:
        text (str): The text to simplify.
        level (str): The target audience level (e.g., '5th grader', 'beginner').

    Returns:
        str: The simplified text or an error message.
    """
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={Config.GEMINI_API_KEY}'
    
    headers = {
        'Content-Type': 'application/json'
    }

    prompt = f"Simplify this text for a {level}: {text}"
    
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        # Optional: Add generation config for more control
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1024
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status() 

        # Using .get() is safer than direct key access and avoids some KeyErrors
        candidates = response.json().get('candidates', [])
        if candidates and 'content' in candidates[0] and 'parts' in candidates[0]['content']:
            return candidates[0]['content']['parts'][0]['text'].strip()
        else:
            return "Error: Unexpected response format from API."

    except requests.exceptions.RequestException as e:
        # Handle network errors, timeouts, and bad status codes
        error_message = f"Error: {e}"
        try:
            # Try to get the specific error message from the API response
            error_details = e.response.json()
            error_message = error_details.get('error', {}).get('message', str(e))
        except (ValueError, AttributeError):
            # If the response isn't JSON or is malformed, stick with the original exception
            pass
        return f"API Request Failed: {error_message}"

# Example Usage:
# Assuming you have a config.py with:
# class Config:
#     GEMINI_API_KEY = "YOUR_API_KEY_HERE"

# sample_text = "The legislative body is currently deliberating on the proposed fiscal amendments."
# simplification_level = "10-year-old"
# simplified = simplify_text(sample_text, simplification_level)
# print(simplified)