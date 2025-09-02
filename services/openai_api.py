# services/openai_api.py
import os
import logging

logger = logging.getLogger(__name__)

try:
    import openai
except Exception:
    openai = None
    logger.warning("OpenAI SDK not available in environment (openai package missing).")

class OpenAISimplifier:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model
        if self.api_key and openai:
            openai.api_key = self.api_key
        elif not self.api_key:
            logger.warning("⚠️ OPENAI_API_KEY not configured; OpenAI fallback will return errors.")

    def simplify(self, text: str, level: str = "layman") -> str:
        """
        Use OpenAI as the final fallback. Returns a string.
        If OpenAI is not configured or an error occurs, returns a '⚠️' prefixed string.
        """
        if not self.api_key:
            return "⚠️ OpenAI API key not configured."

        if openai is None:
            return "⚠️ OpenAI SDK not installed."

        prompt = (
            f"You are LearnBot, an experienced AI teacher. Explain the following text for a {level} learner.\n\n"
            f"Text:\n{text}\n\n"
            "Give a clear, structured, and concise explanation suitable for a tertiary student."
        )

        try:
            # Use chat completion if available
            # This uses the OpenAI Python client - adjust model if needed
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            # Extract text safely
            choices = response.get("choices") or []
            if choices and "message" in choices[0] and "content" in choices[0]["message"]:
                return choices[0]["message"]["content"].strip()
            # older completion format fallback
            if choices and "text" in choices[0]:
                return choices[0]["text"].strip()
            logger.error("OpenAI returned unexpected response: %s", response)
            return "⚠️ OpenAI returned unexpected format."
        except Exception as e:
            logger.exception("OpenAI simplify call failed")
            return f"⚠️ OpenAI error: {str(e)}"
