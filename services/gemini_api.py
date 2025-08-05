import logging
from typing import Optional
import requests
from config.config import Config

logger = logging.getLogger(__name__)

class TextSimplifier:
    """
    Client for Google Gemini generateContent API to simplify text.
    """
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

    def __init__(self, timeout: float = 15.0):
        self.timeout = Config.GEMINI_TIMEOUT or timeout
        self.api_key = Config.GEMINI_API_KEY
        self.session = requests.Session()

    def simplify_text(self, text: str, level: str) -> Optional[str]:
        prompt = (
            f"You are an AI teacher with 20 years of experience. Summarize and simplify the following academic text for a {level} student. Use plain English and make it very easy to understand. "
            "Avoid long paragraphs, unnecessary repetition, or overexplaining. Keep it short but meaningful. "
            "Make sure the important ideas are not removed. Think like you're helping a confused student understand quickly and clearly:\n\n"
            f"{text}"
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        try:
            logger.debug("Sending Payload: %s", payload)
            response = self.session.post(
                f"{self.BASE_URL}?key={self.api_key}",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            logger.debug("API Response: %s", response.text)
        except requests.RequestException as e:
            logger.error("Network error during simplify_text: %s", e)
            return None

        try:
            data = response.json()
            candidates = data.get("candidates")
            if candidates and isinstance(candidates, list) and len(candidates) > 0:
                content = candidates[0].get("content", {})
                parts = content.get("parts")
                if parts and isinstance(parts, list) and len(parts) > 0:
                    return parts[0].get("text")
            logger.error("Missing expected fields in API response: %s", response.text)
            return None
        except (ValueError, TypeError) as e:
            logger.error("Error parsing response JSON: %s — Response was: %s", e, response.text)
            return None
