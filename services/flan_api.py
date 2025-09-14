# services/openrouter_api.py
import logging
import time
from typing import Optional, Dict, Any
import requests
from config.config import Config  # matches your existing pattern
from services.exceptions import RateLimitError, APIError, NetworkError

logger = logging.getLogger(__name__)

# Audience mapping to include in the system instruction
LEVEL_PROMPTS = {
    "layman": "Explain this in simple, clear terms for an adult layperson. Use common words and short sentences.",
    "12yo": "Explain this as if speaking to a 12-year-old student. Use short sentences, examples, and avoid technical jargon.",
    "ss2": "Explain this to a senior secondary school (SS2) student. Keep key terms but define them simply.",
}

SYSTEM_PROMPT_BASE = (
    "You are LearnBot, an educational assistant that simplifies and explains content while preserving meaning and key terms. "
    "Avoid hallucinations and never invent facts. Output in two sections:\n\n"
    "1) Simple Explanation (one short paragraph, <=150 words)\n"
    "2) Key Points (3-5 bullets summarizing the core ideas)\n\n"
    "If asked to provide examples or analogies, keep them brief and relatable."
)

class TextSimplifier:
    """
    OpenRouter TextSimplifier that mirrors your Gemini TextSimplifier interface.
    Uses requests so it fits environments similar to the Gemini implementation.
    """

    def __init__(self, timeout: float = None):
        # Use Config keys (add these to your config file / environment)
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = getattr(Config, "OPENROUTER_BASE_URL", None) or "https://openrouter.ai/api/v1"
        # default path - adjust if your OpenRouter docs require different endpoint
        self.chat_path = getattr(Config, "OPENROUTER_CHAT_PATH", "/chat/completions")
        self.model = getattr(Config, "OPENROUTER_MODEL", "openai/gpt-oss-120b:free")
        self.timeout = timeout or getattr(Config, "OPENROUTER_TIMEOUT", 20.0)
        self.session = requests.Session()

        # optional headers you requested (leaderboard/metadata)
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
        """
        Defensive parsing: try common response shapes:
        - OpenAI-like chat completions: choices[0].message.content
        - choices[0].text
        - top-level 'output' or 'response' fields
        - 'candidates' (huggingface-like)
        """
        # 1) choices -> message.content
        choices = resp_json.get("choices") or resp_json.get("outputs") or []
        if choices and isinstance(choices, list):
            first = choices[0]
            # nested message.content (OpenAI chat format)
            if isinstance(first, dict):
                msg = first.get("message") or first.get("delta") or first.get("output")
                if isinstance(msg, dict) and "content" in msg:
                    # content can be list or str depending on provider
                    content = msg["content"]
                    if isinstance(content, list) and len(content) > 0:
                        # content elements often have 'text'
                        c0 = content[0]
                        if isinstance(c0, dict) and "text" in c0:
                            return c0["text"].strip()
                        elif isinstance(c0, str):
                            return c0.strip()
                    elif isinstance(content, str):
                        return content.strip()
                # fallback: choices[].text
                if "text" in first and isinstance(first["text"], str):
                    return first["text"].strip()
                # fallback: choices[].message.content (older shapes)
                if "message" in first and isinstance(first["message"], dict):
                    cont = first["message"].get("content")
                    if isinstance(cont, str):
                        return cont.strip()
        # 2) direct fields
        for key in ("output", "response", "result", "summary"):
            val = resp_json.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
        # 3) huggingface-like candidates
        candidates = resp_json.get("candidates")
        if candidates and isinstance(candidates, list) and len(candidates) > 0:
            c0 = candidates[0]
            if isinstance(c0, dict) and "content" in c0:
                parts = c0["content"].get("parts") if isinstance(c0["content"], dict) else None
                if parts and isinstance(parts, list) and len(parts) > 0:
                    if isinstance(parts[0], dict) and "text" in parts[0]:
                        return parts[0]["text"].strip()
            # fallback to candidate text
            if isinstance(c0, dict) and "text" in c0:
                return c0["text"].strip()
        return None

    def simplify_text(self, text: str, level: str) -> Optional[str]:
        """
        Sends a simplification request to OpenRouter (OpenAI-compatible). Returns simplified text or
        a friendly error string similar to the Gemini implementation.
        """
        if not text or not text.strip():
            return "⚠️ Text is required."

        prompt = self._build_prompt(text.strip(), level)
        payload = {
            # This payload is OpenAI-like. If your OpenRouter endpoint expects a different shape,
            # set Config.OPENROUTER_CHAT_PATH accordingly or adapt this payload.
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

        # Retry logic for rate limits (429). Exponential backoff.
        max_retries = int(getattr(Config, "OPENROUTER_MAX_RETRIES", 3))
        backoff_base = float(getattr(Config, "OPENROUTER_BACKOFF_BASE", 1.0))
        for attempt in range(1, max_retries + 1):
            try:
                response = self._post(payload, headers)
                status = response.status_code
                if status == 429:
                    # rate limited — log and retry (or bubble up depending on your fallback logic)
                    logger.warning("OpenRouter rate-limited (429). attempt=%d/%d", attempt, max_retries)
                    if attempt == max_retries:
                        return "⚠️ OpenRouter is rate-limited. Please try again later."
                    sleep_for = backoff_base * (2 ** (attempt - 1))
                    time.sleep(sleep_for)
                    continue
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                logger.error("❌ HTTP error calling OpenRouter: %s; Status: %s; Body: %s", e, 
                             getattr(e.response, "status_code", None), getattr(e.response, "text", None))
                # If non-429, return a user-visible message to match Gemini behavior
                return "⚠️ OpenRouter API returned an HTTP error. Please try again."
            except requests.RequestException as e:
                logger.error("❌ Network error during OpenRouter call: %s", e)
                return "⚠️ Network error occurred. Please check your connection and try again."

            # parse JSON defensively
            try:
                resp_json = response.json()
            except Exception:
                logger.exception("Failed to decode OpenRouter JSON response. Raw text: %s", response.text)
                return "⚠️ Unexpected response format from OpenRouter."

            # Attempt to extract assistant text
            simplified = self._parse_response(resp_json)
            if simplified:
                return simplified

            # If parsing failed, log full response for debugging and return informative message
            logger.error("⚠️ Could not parse OpenRouter response into text. Raw JSON: %s", resp_json)
            return "⚠️ Unexpected OpenRouter response format. Check server logs."

        # If loop exits unexpectedly
        return "⚠️ OpenRouter request failed after retries."



""" from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class T5Simplifier:
    def __init__(self, model_name="google/flan-t5-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def simplify(self, text, level="layman"):
        prompt = f"Simplify this for a {level} level: {text}"
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        outputs = self.model.generate(**inputs, max_new_tokens=150)
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result """

""" from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

class T5Simplifier:
    def __init__(self):
        model_name = "google/flan-t5-base"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def simplify(self, text, level):
        # Generate prompt based on simplification level
        prompt = f"Simplify this text for a {level} level: {text}"

        # Tokenize and generate output
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        outputs = self.model.generate(
            **inputs,
            max_length=512,
            num_beams=4,
            early_stopping=True
        )

        # Decode and return the output
        simplified_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return simplified_text """


""" 
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class T5Simplifier:
    def __init__(self, model_name="google/flan-t5-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def simplify(self, text, level="layman"):
        # Improved prompt for better simplification
        prompt = (
            f"Simplify this text in very easy terms for a {level}-level learner. "
            f"Only give the simplified version. Text:\n\n{text}"
        )

        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            num_beams=4,
            early_stopping=True
        )

        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result.strip() """