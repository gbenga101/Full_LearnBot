from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyCS2yadT9SkwdNvoOHoKHnR8hNZzFcrGIQpyh')
    GEMINI_TIMEOUT = float(os.getenv('GEMINI_TIMEOUT', 15.0))
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')