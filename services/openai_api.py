""" import os
import requests
import logging

logger = logging.getLogger(__name__)

class OpenAISimplifier:
    API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
    MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")  # replace with your preferred model
    TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "15"))

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set in environment")

    def simplify_text(self, text: str, level: str) -> str:
        prompt = (
            f"You are an experienced teacher. Summarize and simplify this for a {level} student. "
            "Use plain language, short paragraphs, and keep the important ideas intact:\n\n" + text
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.2
        }

        resp = requests.post(self.API_URL, headers=headers, json=payload, timeout=self.TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        # Typical Chat Completion parsing
        try:
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.exception("Unexpected OpenAI response format: %s", data)
            raise """

# services/openai_api.py
import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)

try:
    # lazy import to avoid failing if package not installed
    from openai import OpenAI  # if you plan to use openai-python later
except Exception:
    OpenAI = None

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