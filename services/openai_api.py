# services/openai_api.py
import logging
import os
from typing import Optional, Any

from config.config import Config
from services.exceptions import RateLimitError, APIError, NetworkError

logger = logging.getLogger(__name__)

# Try to support both the modern OpenAI client and the legacy openai package.
_new_client_cls = None
_legacy_module = None
_OpenAIRateLimit = None
_OpenAIGeneric = Exception

try:
    # modern openai v1+ client
    from openai import OpenAI as OpenAIClient  # type: ignore
    _new_client_cls = OpenAIClient
    import openai as _openai_mod  # get exception classes if available
    _OpenAIRateLimit = getattr(_openai_mod, "RateLimitError", None) or getattr(getattr(_openai_mod, "error", None), "RateLimitError", None)
    _OpenAIGeneric = getattr(_openai_mod, "OpenAIError", Exception)
except Exception:
    _new_client_cls = None
    try:
        # legacy openai package (pre-v1)
        import openai as _legacy  # type: ignore
        _legacy_module = _legacy
        _OpenAIRateLimit = getattr(_legacy, "RateLimitError", None) or getattr(getattr(_legacy, "error", None), "RateLimitError", None)
        _OpenAIGeneric = getattr(_legacy, "OpenAIError", Exception)
    except Exception:
        _legacy_module = None
        _OpenAIRateLimit = None
        _OpenAIGeneric = Exception

if not _new_client_cls and not _legacy_module:
    logger.warning("OpenAI SDK not available in environment (openai package missing).")


def _extract_text_from_choice(choice: Any) -> Optional[str]:
    """
    Try many common shapes for a 'choice' element and return text content if found.
    Handles:
      - object choices with .message.content
      - dict choices with ['message']['content'] or ['text']
      - choices with nested 'content' lists/parts
      - 'delta' streaming pieces (if present)
    """
    try:
        # 1) if it's an object with .message.content
        msg = getattr(choice, "message", None)
        if msg is not None:
            # msg might be an object with .content attr or a list/dict
            content = getattr(msg, "content", None)
            if isinstance(content, str) and content.strip():
                return content.strip()
            # sometimes message.content is a list of dicts
            if isinstance(content, list) and len(content) > 0:
                first = content[0]
                if isinstance(first, dict) and isinstance(first.get("text"), str):
                    return first.get("text").strip()
                if isinstance(first, str):
                    return first.strip()

        # 2) if choice itself has 'text' attr
        text_attr = getattr(choice, "text", None)
        if isinstance(text_attr, str) and text_attr.strip():
            return text_attr.strip()

        # 3) if it's a dict-like structure
        if isinstance(choice, dict):
            # nested message.content
            message = choice.get("message")
            if isinstance(message, dict):
                # message.content can be str or list
                cont = message.get("content")
                if isinstance(cont, str) and cont.strip():
                    return cont.strip()
                if isinstance(cont, list) and len(cont) > 0:
                    first = cont[0]
                    if isinstance(first, dict) and isinstance(first.get("text"), str):
                        return first.get("text").strip()
                    if isinstance(first, str):
                        return first.strip()
            # older fallback keys
            for k in ("text", "content", "output", "summary", "response"):
                v = choice.get(k)
                if isinstance(v, str) and v.strip():
                    return v.strip()

        # 4) streaming 'delta' shape - try delta.content or delta.get('content')
        delta = getattr(choice, "delta", None) or (choice.get("delta") if isinstance(choice, dict) else None)
        if isinstance(delta, dict):
            # delta content might be list/dict/str
            cont = delta.get("content")
            if isinstance(cont, str) and cont.strip():
                return cont.strip()

        # 5) last resort: str(choice) sanitized (avoid dumping huge objects)
        try:
            s = str(choice)
            if isinstance(s, str) and len(s) > 0 and len(s) < 2000:
                return s.strip()
        except Exception:
            pass

    except Exception:
        # be defensive: don't let parsing errors bubble here
        logger.exception("Exception while extracting text from choice: %s", choice)
    return None


def _extract_text_from_response(resp: Any) -> Optional[str]:
    """
    Try multiple response shapes:
      - resp.to_dict() if available
      - resp.choices list of objects
      - resp['choices'] if dict
    """
    # 1) try to convert to dict if possible
    try:
        if hasattr(resp, "to_dict") and callable(getattr(resp, "to_dict")):
            d = resp.to_dict()
            # reuse dict parsing below
            resp = d
    except Exception:
        # ignore conversion failures
        logger.debug("Could not call to_dict() on response", exc_info=True)

    # 2) if dict-like
    if isinstance(resp, dict):
        choices = resp.get("choices") or resp.get("outputs") or []
        if isinstance(choices, list):
            for c in choices:
                txt = _extract_text_from_choice(c)
                if txt:
                    return txt
        # other top-level keys
        for k in ("output", "response", "result", "summary"):
            v = resp.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
        return None

    # 3) if object with attribute .choices
    choices = getattr(resp, "choices", None)
    if choices and isinstance(choices, (list, tuple)):
        for c in choices:
            txt = _extract_text_from_choice(c)
            if txt:
                return txt

    # 4) fallback None
    return None


class OpenAISimplifier:
    """
    OpenAI adapter that:
     - supports new (OpenAI) client and legacy openai package
     - raises typed provider exceptions (RateLimitError, APIError, NetworkError)
     - uses Config.OPENAI_MODEL and Config.OPENAI_MAX_TOKENS
     - preserves the 'layman' and '12yo' prompt formats used by your frontend
    """

    def __init__(self, model: Optional[str] = None):
        self.api_key = getattr(Config, "OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", None))
        self.model = model or getattr(Config, "OPENAI_MODEL", os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"))
        self.max_tokens = int(getattr(Config, "OPENAI_MAX_TOKENS", os.getenv("OPENAI_MAX_TOKENS", 450)))

        # Try a safe instantiation method: set env var then instantiate client without passing api_key
        self._client = None
        if _new_client_cls and self.api_key:
            try:
                os.environ.setdefault("OPENAI_API_KEY", self.api_key)
                self._client = _new_client_cls()
            except Exception:
                logger.exception("Failed to instantiate new OpenAI client (safe path); will fallback to legacy module if present.")
                self._client = None

        # configure legacy module if present
        self._legacy = _legacy_module
        if self._legacy and self.api_key:
            try:
                self._legacy.api_key = self.api_key
            except Exception:
                pass

        if not self.api_key:
            logger.warning("⚠️ OPENAI_API_KEY not configured; OpenAI fallback will not work until set.")
        if not (self._client or self._legacy):
            logger.warning("⚠️ OpenAI SDK not available or failed to init; OpenAI fallback will not work.")

    def _build_messages(self, text: str, level: str):
        # Keep your SYSTEM prompt and audience instructions (layman / 12yo) exactly as provided
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

        LEVEL_PROMPTS = {
            "layman": (
                "Explain this for a learner who needs clear and accessible content, such as a senior secondary school (SS2) student or an adult with no background in the topic. "
                "Use simple, everyday words and short sentences to ensure clarity. Keep key subject terms but define them simply in plain language. "
                "Include a brief, relatable example or analogy to make concepts easier to understand. "
                "Balance simplicity with academic accuracy to support learning core subjects without losing essential details."
            ),
            "12yo": (
                "Explain this as if teaching a 12-year-old student. Use short, simple sentences and a fun, relatable example or analogy. "
                "Avoid technical terms or explain them clearly within the explanation paragraph in a way a child would understand."
            ),
        }

        lvl = level if level in LEVEL_PROMPTS else "layman"
        lvl_instr = LEVEL_PROMPTS.get(lvl, LEVEL_PROMPTS["layman"])
        user_text = f"Audience instruction: {lvl_instr}\n\nUser text:\n{text}"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_BASE},
            {"role": "user", "content": user_text},
        ]
        return messages

    def simplify(self, text: str, level: str = "layman") -> str:
        """
        Simplify text using OpenAI. Returns simplified text or raises Provider exceptions.
        """
        if not text or not text.strip():
            raise APIError("Input text is empty")

        if not (self._client or self._legacy):
            raise APIError("OpenAI SDK not installed in environment")

        messages = self._build_messages(text.strip(), level)

        # 1) Try modern client first
        if self._client:
            try:
                resp = self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=0.2,
                )
            except Exception as e:
                serr = str(e)
                if _OpenAIRateLimit and isinstance(e, _OpenAIRateLimit):
                    logger.warning("OpenAI rate-limited (new client): %s", e)
                    raise RateLimitError(serr)
                if isinstance(e, _OpenAIGeneric):
                    logger.exception("OpenAI API error (new client): %s", e)
                    raise APIError(serr)
                logger.exception("Network/OpenAI SDK error (new client): %s", e)
                raise NetworkError(serr)

            # parse modern client response (robust)
            try:
                text_out = _extract_text_from_response(resp)
                if text_out:
                    return text_out
                logger.error("OpenAI (new client) returned unexpected response shape: %s", resp)
                raise APIError("OpenAI returned unexpected format (new client)")
            except APIError:
                raise
            except Exception as e:
                logger.exception("Failed to parse OpenAI (new client) response: %s", e)
                raise APIError("Failed to parse OpenAI response (new client)")

        # 2) Fallback to legacy client if present
        if self._legacy:
            try:
                resp = self._legacy.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=0.2,
                )
            except Exception as e:
                serr = str(e)
                if _OpenAIRateLimit and isinstance(e, _OpenAIRateLimit):
                    logger.warning("OpenAI rate-limited (legacy client): %s", e)
                    raise RateLimitError(serr)
                logger.exception("OpenAI API error (legacy client): %s", e)
                raise APIError(serr)

            # parse legacy response
            try:
                text_out = _extract_text_from_response(resp)
                if text_out:
                    return text_out
                logger.error("OpenAI (legacy) returned unexpected response: %s", resp)
                raise APIError("OpenAI returned unexpected format (legacy client)")
            except APIError:
                raise
            except Exception as e:
                logger.exception("Failed to parse OpenAI (legacy) response: %s", e)
                raise APIError("Failed to parse OpenAI response (legacy client)")

        # if neither client produced a response
        raise APIError("OpenAI client not available")