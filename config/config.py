from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_TIMEOUT = float(os.getenv('GEMINI_TIMEOUT', 15.0))

    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'openai/gpt-oss-120b:free')
    OPENROUTER_CHAT_PATH = os.getenv('OPENROUTER_CHAT_PATH', '/chat/completions')
    OPENROUTER_TIMEOUT = float(os.getenv('OPENROUTER_TIMEOUT', 20))
    OPENROUTER_MAX_RETRIES = int(os.getenv('OPENROUTER_MAX_RETRIES', 3))
    OPENROUTER_BACKOFF_BASE = float(os.getenv('OPENROUTER_BACKOFF_BASE', 2.0))
    OPENROUTER_HTTP_REFERER = os.getenv('OPENROUTER_HTTP_REFERER', 'https://gbenga101.github.io/LearnBot/')
    OPENROUTER_X_TITLE = os.getenv('OPENROUTER_X_TITLE', 'LearnBot')
    
    #FILE UPLOAD
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    
    #OpenAI Fallback (FINAL)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", 450))
