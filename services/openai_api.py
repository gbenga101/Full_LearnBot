# services/openai_api.py
import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)

class OpenAISimplifier:
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY if hasattr(Config, 'OPENAI_API_KEY') else os.getenv('OPENAI_API_KEY', '')
        # If you later want to use the SDK, initialize here:
        # if self.api_key and OpenAI:
        #     self.client = OpenAI(api_key=self.api_key)
        # else:
        #     self.client = None

    def simplify_text(self, text: str, level: str) -> Optional[str]:
        """
        Minimal safe stub. If OPENAI_API_KEY is set, you can replace this body with an actual call.
        For now: return clear placeholder if key is missing so frontend won't crash.
        """
        if not self.api_key:
            logger.info("OpenAI API key not configured — returning placeholder.")
            return "[OpenAI fallback inactive: no API key configured on server]"

        # TODO: Replace with actual OpenAI call (ChatCompletions / responses) when you add a key.
        # Keep this block simple, return a short placeholder for now to avoid errors.
        logger.info("OpenAI API key present but real call is not implemented in stub.")
        return "[OpenAI fallback stub: key found but call not implemented]"
# services/openai_api.py
""" try:
    # lazy import to avoid failing if package not installed
    from openai import OpenAI  # if you plan to use openai-python later
except Exception:
    OpenAI = None
 """
from config.config import Config

class OpenAISimplifier:
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY if hasattr(Config, 'OPENAI_API_KEY') else os.getenv('OPENAI_API_KEY', '')
        # If you later want to use the SDK, initialize here:
        # if self.api_key and OpenAI:
        #     self.client = OpenAI(api_key=self.api_key)
        # else:
        #     self.client = None

    def simplify_text(self, text: str, level: str) -> Optional[str]:
        """
        Minimal safe stub. If OPENAI_API_KEY is set, you can replace this body with an actual call.
        For now: return clear placeholder if key is missing so frontend won't crash.
        """
        if not self.api_key:
            logger.info("OpenAI API key not configured — returning placeholder.")
            return "[OpenAI fallback inactive: no API key configured on server]"

        # TODO: Replace with actual OpenAI call (ChatCompletions / responses) when you add a key.
        # Keep this block simple, return a short placeholder for now to avoid errors.
        logger.info("OpenAI API key present but real call is not implemented in stub.")
        return "[OpenAI fallback stub: key found but call not implemented]"
