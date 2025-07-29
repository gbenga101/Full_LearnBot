import requests
import os
import sys

# 1. Load the API key from an environment variable for security
API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyCS2yadT9SkwdNvoOHoKHnR8hNZzFcrGIQ')  # Default for testing, replace with your key later

# Check if the API key is available
if not API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set.")
    sys.exit(1) # Exit the script if the key is missing

# --- API Configuration ---
url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}'
headers = {'Content-Type': 'application/json'}
data = {
    "contents": [{
        "parts": [{
            "text": "Say hello in English."
        }]
    }]
}

# --- Make the API Request ---
response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    # 2. Safely parse the JSON response
    try:
        json_response = response.json()
        text = json_response['candidates'][0]['content']['parts'][0]['text']
        print(text)
    except (KeyError, IndexError, TypeError):
        print("Error: Failed to parse the API response.")
        print("Full Response:", response.text)
else:
    # This error handling is good! It shows the status and API error message.
    print(f"Error: {response.status_code}, {response.text}")