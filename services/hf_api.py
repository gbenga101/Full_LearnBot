# services/hf_api.py
import os
import requests
import logging

logger = logging.getLogger(__name__)
HF_TOKEN = os.getenv("HF_API_KEY")  # set this on Render / env

class HFSimplifier:
    def __init__(self, model: str = "google/flan-t5-small"):
        self.model = model
        if not HF_TOKEN:
            logger.warning("HF_API_KEY not found in env. HFSimplifier will fail until key is set.")

    def simplify(self, text: str, level: str = "layman", max_new_tokens: int = 256) -> str:
        if not HF_TOKEN:
            return "⚠️ Hugging Face API key not configured."

        prompt = f"Simplify for tertiary students (level={level}):\n\n{text}"
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": max_new_tokens}
        }
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        try:
            resp = requests.post(
                f"https://api-inference.huggingface.co/models/{self.model}",
                headers=headers,
                json=payload,
                timeout=30
            )
            resp.raise_for_status()
            out = resp.json()
            if isinstance(out, list) and out and "generated_text" in out[0]:
                return out[0]["generated_text"]
            if isinstance(out, dict) and "generated_text" in out:
                return out["generated_text"]
            return str(out)
        except requests.RequestException as e:
            logger.exception("Hugging Face inference request failed")
            return f"⚠️ HF request failed: {str(e)}"
