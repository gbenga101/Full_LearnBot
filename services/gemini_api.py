""" import logging
from typing import Optional
import requests
from config.config import Config

logger = logging.getLogger(__name__)

class TextSimplifier:
    
    #Client for Google Gemini generateContent API to simplify text.

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

    def __init__(self, timeout: float = 15.0):
        self.timeout = Config.GEMINI_TIMEOUT or timeout
        self.api_key = Config.GEMINI_API_KEY
        self.session = requests.Session()

    def simplify_text(self, text: str, level: str) -> Optional[str]:
        prompt = (
            f"You are an AI teacher with 20 years of experience. Summarize and simplify the following academic text for a {level} student. "
            "Use plain English and make it very easy to understand. "
            "Avoid long paragraphs, unnecessary repetition, or overexplaining. Keep it short but meaningful. "
            "Make sure the important ideas are not removed. Think like you're helping a confused student understand quickly and clearly:\n\n"
            f"{text}"
        )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        { "text": prompt }
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
            if candidates and isinstance(candidates, list):
                for candidate in candidates:
                    parts = candidate.get("content", {}).get("parts", [])
                    if parts and isinstance(parts, list):
                        return parts[0].get("text")
            logger.error("Missing expected fields in API response: %s", response.text)
            return None
        except Exception as e:
            logger.error("Error parsing response JSON: %s — Response was: %s", e, response.text)
            return None """

import logging
from typing import Optional
import requests
from config.config import Config

logger = logging.getLogger(__name__)

class TextSimplifier:
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

    def __init__(self, timeout: float = 15.0):
        self.timeout = Config.GEMINI_TIMEOUT or timeout
        self.api_key = Config.GEMINI_API_KEY
        self.session = requests.Session()

        if not self.api_key:
            logger.warning("⚠️ GEMINI_API_KEY is missing in your config.")

    def simplify_text(self, text: str, level: str) -> Optional[str]:
        """
        Sends a prompt to Gemini API to summarize and simplify academic text.
        :param text: The academic text to simplify.
        :param level: Target explanation level (e.g., 'layman', '12-year-old').
        :return: Simplified explanation or None if an error occurred.
        """
        prompt = (
            f"You are an AI teacher with 20 years of experience. Summarize and simplify the following academic text for a {level} student. "
            "Use plain English and make it very easy to understand. "
            "Avoid long paragraphs, unnecessary repetition, or overexplaining. Keep it short but meaningful. "
            "Make sure the important ideas are not removed. Think like you're helping a confused student understand quickly and clearly:\n\n"
            f"{text}"
        )

        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": prompt}]
            }]
        }

        try:
            logger.debug("📤 Sending to Gemini API: %s", payload)
            response = self.session.post(
                f"{self.BASE_URL}?key={self.api_key}",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error("❌ HTTP error during Gemini call: %s", e)
            return "⚠️ Gemini API returned an HTTP error. Please try again."
        except requests.RequestException as e:
            logger.error("❌ Network error during Gemini call: %s", e)
            return "⚠️ Network error occurred. Please check your connection and try again."

        try:
            data = response.json()
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            return parts[0].get("text") if parts else "⚠️ No explanation returned by Gemini."
        except Exception as e:
            logger.error("❌ Failed to parse Gemini response: %s\nRaw response: %s", e, response.text)
            return "⚠️ Unexpected response format from Gemini API."