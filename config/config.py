""" import os

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  # WARNING: Never hardcode sensitive information like API keys in source code. Use environment variables instead.
    if GEMINI_API_KEY is None:
        raise ValueError("GEMINI_API_KEY environment variable must be set")
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')  # Configurable upload folder with default

 """
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyCS2yadT9SkwdNvoOHoKHnR8hNZzFcrGIQ')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')