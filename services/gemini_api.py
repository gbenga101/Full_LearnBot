import logging
from typing import Optional
import requests
from config.config import Config

logger = logging.getLogger(__name__)

class TextSimplifier:
    """
    Client for Google Gemini generateContent API to simplify text.
    """
    BASE_URL = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-1.5-flash-latest:generateContent"
    )

    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        self.api_key = Config.GEMINI_API_KEY  # Use Config's key
        self.session = requests.Session()

    def simplify_text(self, text: str, level: str) -> Optional[str]:
        """
        Simplifies the given text to the specified reading level.
        :param text: Original text to simplify.
        :param level: Target reading level (e.g., "elementary", "high school").
        :return: Simplified text, or None if an error occurred.
        """
        prompt = f"Take the following complex text and simplify it for a {level} audience: '{text}'. Return only the simplified version, no additional instructions or prompts."
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
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
            logger.debug("Parsed Data: %s", data)
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