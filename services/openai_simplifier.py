import os
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
            raise
