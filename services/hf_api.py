# services/hf_api.py
import os
import requests
import logging

logger = logging.getLogger(__name__)

class HFSimplifier:
    def __init__(self, model: str = "google/flan-t5-small"):
        self.api_key = os.getenv("HF_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ HF_API_KEY not found in environment. HFSimplifier will return errors until configured.")
        self.model = model
        self.url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    def simplify(self, text: str, level: str = "layman", max_new_tokens: int = 150) -> str:
        if not self.api_key:
            return "⚠️ Hugging Face API key not configured."

        prompt = (
            f"You are a LearnBot, an AI teacher with 20+ years of experience. "
            f"Explain the following text for a {level} learner in the clearest way possible. "
            "Follow these rules:\n"
            "1. Use plain, everyday English.\n"
            "2. Keep it concise but do not skip important details.\n"
            "3. Use short sentences and simple words.\n"
            "4. When possible, give a quick example or analogy to make it relatable.\n"
            "5. Break information into bullet points or steps if it improves clarity.\n"
            "6. Avoid jargon unless you explain it.\n\n"
            f"Text to simplify:\n{text}"
        )

        payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_new_tokens, "temperature": 0.7}}

        try:
            resp = requests.post(self.url, headers=self.headers, json=payload, timeout=60)
            if resp.status_code != 200:
                # Provide consistent error string that triggers fallback logic
                logger.error("Hugging Face returned HTTP %s: %s", resp.status_code, resp.text)
                return f"⚠️ Hugging Face API error: {resp.status_code} - {resp.text}"
            data = resp.json()
            # Expected a list with generated_text
            if isinstance(data, list) and data and "generated_text" in data[0]:
                return data[0]["generated_text"].strip()
            # Some models may return dict with 'generated_text'
            if isinstance(data, dict) and "generated_text" in data:
                return data["generated_text"].strip()
            logger.error("Hugging Face returned unexpected format: %s", data)
            return "⚠️ Hugging Face API returned unexpected format."
        except requests.RequestException as e:
            logger.exception("Hugging Face API request failed")
            return f"⚠️ Hugging Face request exception: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in HFSimplifier.simplify")
            return f"⚠️ Hugging Face internal error: {str(e)}"
