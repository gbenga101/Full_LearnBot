import logging
from typing import Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config.config import Config
from services.exceptions import RateLimitError, APIError, NetworkError

logger = logging.getLogger(__name__)

class TextSimplifier:
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    def __init__(self, timeout: float = 15.0):
        self.timeout = max(float(Config.GEMINI_TIMEOUT or timeout), 1.0)  # Ensure positive timeout
        self.api_key = Config.GEMINI_API_KEY
        self.session = requests.Session()

        if not self.api_key:
            logger.error("⚠️ GEMINI_API_KEY is missing in config.")
            raise APIError("GEMINI_API_KEY is required but not set in config.")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(RateLimitError)
    )
    def simplify_text(self, text: str, level: str) -> str:
        """
        Sends a prompt to Gemini API to simplify academic text for a target audience.
        Returns simplified text or raises Provider exceptions on errors.
        """
        if not text or not text.strip():
            raise APIError("Empty input text")

        prompt = (
            f"You are LearnBot, an AI designed to make complex academic content accessible to learners of all levels. "
            f"Your goal is to summarize and simplify the provided text for a {level} learner, ensuring clarity and engagement. "
            "Follow these guidelines:\n"
            "1. Use simple, conversational English with short sentences.\n"
            "2. Summarize concisely but retain all key concepts and critical details.\n"
            "3. Explain any technical terms or jargon in plain language.\n"
            "4. Include a relatable example, analogy, or metaphor to aid understanding.\n"
            "5. Organize complex ideas into bullet points, steps, or short paragraphs for readability.\n"
            "6. Maintain a friendly, encouraging tone to keep the learner motivated.\n"
            "7. Avoid removing essential information or oversimplifying to the point of inaccuracy.\n\n"
            f"Text to simplify:\n{text}"
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
        except requests.RequestException as e:
            logger.error("❌ Network error during Gemini call: %s", e)
            raise NetworkError(str(e))

        # HTTP layer
        if response.status_code == 429:
            logger.warning("Gemini rate-limited (429). Status: %s", response.status_code)
            raise RateLimitError("Gemini rate-limited (429)")

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error("❌ HTTP error during Gemini call: %s", e)
            raise APIError(f"Gemini HTTP error: {getattr(response, 'status_code', None)} - {getattr(response, 'text', '')}")

        # Parse response
        try:
            data = response.json()
        except Exception as e:
            logger.error("❌ Failed to decode Gemini JSON response: %s\nRaw response: %s", e, response.text)
            raise APIError("Failed to decode Gemini JSON response")

        parts = []
        candidates = data.get("candidates", [])
        for candidate in candidates:
            content = candidate.get("content", {})
            parts.extend(content.get("parts", []))
        if parts:
            text_out = parts[0].get("text")
            if text_out and isinstance(text_out, str) and text_out.strip():
                return text_out.strip()
            else:
                logger.error("❌ Gemini returned empty or malformed parts: %s", parts)
                raise APIError("Gemini returned empty or malformed response")
        else:
            logger.error("❌ No candidates returned by Gemini. Raw JSON: %s", data)
            raise APIError("No candidates returned by Gemini")


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


""" 
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
            return "⚠️ Unexpected response format from Gemini API." """