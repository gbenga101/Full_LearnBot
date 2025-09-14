import logging
import time
from typing import Optional, Dict, Any
import requests
from config.config import Config
from services.exceptions import RateLimitError, APIError, NetworkError
logger = logging.getLogger(__name__)
LEVEL_PROMPTS = {
    "layman": (
        "Explain this for a learner who needs clear and accessible content, such as a senior secondary school (SS2) student or an adult with no background in the topic. "
        "Use simple, everyday words and short sentences to ensure clarity. Keep key subject terms but define them simply in plain language. "
        "Include a brief, relatable example or analogy to make concepts easier to understand. "
        "Balance simplicity with academic accuracy to support learning core subjects without losing essential details."
    ),
    "12yo": (
        "Explain this as if teaching a 12-year-old student. Use short, simple sentences and a fun, relatable example or analogy. "
        "Avoid technical terms or explain them in a way a child would understand."
    ),
    "ss2": (
        "Explain this for a senior secondary school (SS2) student. Use clear language, keep key terms but define them simply, and include a relevant example. "
        "Balance simplicity with academic accuracy."
    ),
}
SYSTEM_PROMPT_BASE = (
    "You are LearnBot, an AI designed to make complex academic content accessible and engaging for learners of all levels. "
    "Your goal is to summarize and simplify the provided text for the specified audience while preserving meaning and key concepts. "
    "Follow these guidelines:\n"
    "1. Use clear, conversational English with short sentences.\n"
    "2. Summarize concisely but retain all critical ideas and details.\n"
    "3. Explain any technical terms or jargon in plain language.\n"
    "4. Include a brief, relatable example or analogy to aid understanding.\n"
    "5. Output in two sections: a) Simple Explanation (one short, complete paragraph starting with a clear introduction, <=150 words), b) Key Points (3-5 bullets summarizing core ideas).\n"
    "6. Maintain a friendly, encouraging tone to keep the learner motivated.\n"
    "7. Avoid inventing facts or oversimplifying to the point of inaccuracy.\n"
    "Respond only with the simplified explanation and key points, nothing else."
)
class TextSimplifier:
    """
    OpenRouter TextSimplifier that mirrors your Gemini TextSimplifier interface.
    Raises Provider exceptions for clean fallback handling.
    """
    def __init__(self, timeout: float = None):
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = getattr(Config, "OPENROUTER_BASE_URL", None) or "https://openrouter.ai/api/v1"
        self.chat_path = getattr(Config, "OPENROUTER_CHAT_PATH", "/chat/completions")
        self.model = getattr(Config, "OPENROUTER_MODEL", "openai/gpt-oss-120b:free")
        self.timeout = timeout or getattr(Config, "OPENROUTER_TIMEOUT", 20.0)
        self.session = requests.Session()
        self.extra_headers = {
            "HTTP-Referer": getattr(Config, "OPENROUTER_HTTP_REFERER", "") or "",
            "X-Title": getattr(Config, "OPENROUTER_X_TITLE", "") or "LearnBot",
        }
        if not self.api_key:
            logger.warning("⚠️ OPENROUTER_API_KEY is missing in your Config (OPENROUTER_API_KEY).")
    def _build_prompt(self, text: str, level: str) -> str:
        lvl = level if level in LEVEL_PROMPTS else "layman"
        lvl_instr = LEVEL_PROMPTS.get(lvl, LEVEL_PROMPTS["layman"])
        prompt = f"{SYSTEM_PROMPT_BASE}\nAudience instruction: {lvl_instr}\n\nUser text:\n{text}"
        return prompt
    def _post(self, payload: Dict[str, Any], headers: Dict[str, str]) -> requests.Response:
        url = self.base_url.rstrip("/") + self.chat_path
        logger.debug("POST %s (model=%s) payload size=%d", url, self.model, len(str(payload)))
        return self.session.post(url, json=payload, headers=headers, timeout=self.timeout)
    def _parse_response(self, resp_json: Dict[str, Any]) -> Optional[str]:
        choices = resp_json.get("choices") or resp_json.get("outputs") or []
        if choices and isinstance(choices, list):
            first = choices[0]
            if isinstance(first, dict):
                msg = first.get("message") or first.get("delta") or first.get("output")
                if isinstance(msg, dict) and "content" in msg:
                    content = msg["content"]
                    if isinstance(content, list) and len(content) > 0:
                        c0 = content[0]
                        if isinstance(c0, dict) and "text" in c0:
                            return c0["text"].strip()
                        elif isinstance(c0, str):
                            return c0.strip()
                    elif isinstance(content, str):
                        return content.strip()
                if "text" in first and isinstance(first["text"], str):
                    return first["text"].strip()
                if "message" in first and isinstance(first["message"], dict):
                    cont = first["message"].get("content")
                    if isinstance(cont, str):
                        return cont.strip()
        for key in ("output", "response", "result", "summary"):
            val = resp_json.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
        candidates = resp_json.get("candidates")
        if candidates and isinstance(candidates, list) and len(candidates) > 0:
            c0 = candidates[0]
            if isinstance(c0, dict) and "content" in c0:
                parts = c0["content"].get("parts") if isinstance(c0["content"], dict) else None
                if parts and isinstance(parts, list) and len(parts) > 0:
                    if isinstance(parts[0], dict) and "text" in parts[0]:
                        return parts[0]["text"].strip()
            if isinstance(c0, dict) and "text" in c0:
                return c0["text"].strip()
        return None
    def simplify_text(self, text: str, level: str) -> str:
        if not text or not text.strip():
            raise APIError("Text is required.")
        prompt = self._build_prompt(text.strip(), level)
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 450,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json",
            **({k: v for k, v in self.extra_headers.items() if v}),
        }
        max_retries = int(getattr(Config, "OPENROUTER_MAX_RETRIES", 3))
        backoff_base = float(getattr(Config, "OPENROUTER_BACKOFF_BASE", 1.0))
        for attempt in range(1, max_retries + 1):
            try:
                response = self._post(payload, headers)
            except requests.RequestException as e:
                logger.error("❌ Network error during OpenRouter call: %s", e)
                raise NetworkError(str(e))
            status = getattr(response, "status_code", None)
            if status == 429:
                logger.warning("OpenRouter rate-limited (429). attempt=%d/%d", attempt, max_retries)
                # If this is the final attempt, raise RateLimitError
                if attempt == max_retries:
                    raise RateLimitError("OpenRouter rate-limited (429)")
                sleep_for = backoff_base * (2 ** (attempt - 1))
                time.sleep(sleep_for)
                continue
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logger.error("❌ HTTP error calling OpenRouter: %s; Status: %s; Body: %s", e, getattr(response, "status_code", None), getattr(response, "text", None))
                raise APIError(f"OpenRouter HTTP error: {getattr(response, 'status_code', None)} - {getattr(response, 'text', '')}")
            try:
                resp_json = response.json()
            except Exception:
                logger.exception("Failed to decode OpenRouter JSON response. Raw text: %s", getattr(response, "text", None))
                raise APIError("Failed to decode OpenRouter JSON response")
            simplified = self._parse_response(resp_json)
            if simplified:
                return simplified
            logger.error("⚠️ Could not parse OpenRouter response into text. Raw JSON: %s", resp_json)
            raise APIError("Unexpected OpenRouter response format")
        # If somehow loop finishes without returning, raise APIError
        raise APIError("OpenRouter request failed after retries")



""" import os, requests, logging

logger = logging.getLogger(__name__)

class HFSimplifier:
    def __init__(self):
        self.api_key = os.getenv("HF_API_KEY")
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        self.api_url = "https://api-inference.huggingface.co/models"
        # Try these in order until one works
        self.models = [
            "facebook/bart-large-cnn",
            "google/flan-t5-base",
            "google/flan-t5-small",
        ]

    def simplify(self, text: str, level: str) -> str:
        if not self.api_key:
            return "⚠️ Hugging Face API key not configured."

        prompt = (
            f"LearnBot is an AI teacher with 20+ years of experience. "
            f"Explain the following text for a {level} learner in the clearest way possible. "
            f"Be concise, use simple words, and give a short example if helpful.\n\n"
            f"Text to simplify: {text}"
        )

        for model in self.models:
            try:
                logger.debug("📡 Trying HF model: %s", model)
                resp = requests.post(
                    f"{self.api_url}/{model}",
                    headers=self.headers,
                    json={"inputs": prompt},
                    timeout=30
                )
                if resp.status_code != 200:
                    logger.debug("HF model %s returned %s", model, resp.status_code)
                    continue

                data = resp.json()
                logger.debug("HF raw response: %s", data)

                # Normalize response
                simplified = None
                if isinstance(data, list):
                    texts = []
                    for item in data:
                        if isinstance(item, dict):
                            if "summary_text" in item:
                                texts.append(item["summary_text"])
                            elif "generated_text" in item:
                                texts.append(item["generated_text"])
                    simplified = " ".join(texts).strip() if texts else None
                elif isinstance(data, dict):
                    simplified = data.get("summary_text") or data.get("generated_text")

                if simplified:
                    logger.info("✅ Hugging Face model %s succeeded", model)
                    return simplified

            except Exception as e:
                logger.warning("HF model %s failed: %s", model, e)

        return "⚠️ All Hugging Face models failed."
 """