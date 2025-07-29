from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyCS2yadT9SkwdNvoOHoKHnR8hNZzFcrGIQpyh')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')