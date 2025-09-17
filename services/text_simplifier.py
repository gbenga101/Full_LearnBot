# services/text_simplifier.py
"""
Unified simplifier entrypoint.
Provider chain (default / auto): Gemini -> OpenRouter -> OpenAI
You can request a specific provider by name: "gemini", "openrouter", "openai".
Adapters are expected to raise typed exceptions from services.exceptions
(e.g. RateLimitError, ProviderError, APIError, NetworkError).
This wrapper will attempt fallback on exceptions or empty/invalid returns.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# adapters (may raise at import if not available; we handle lazily)
from services.exceptions import RateLimitError, APIError, NetworkError, ProviderError

def _call_adapter(adapter, text: str, level: str = "layman") -> Optional[str]:
    """
    Call adapter using a best-effort method name resolution.
    Looks for: simplify_text(), simplify(), or __call__.
    Returns string on success or None on parse/empty.
    """
    if adapter is None:
        return None

    # decide the callable
    fn = None
    for name in ("simplify_text", "simplify", "__call__"):
        if hasattr(adapter, name):
            fn = getattr(adapter, name)
            break

    if fn is None:
        # maybe adapter itself is callable
        if callable(adapter):
            fn = adapter
        else:
            raise ProviderError("Adapter has no callable simplifier method")

    try:
        # guard: some adapters expect (text, level), others only (text)
        import inspect
        sig = inspect.signature(fn)
        if len(sig.parameters) >= 2:
            res = fn(text, level)
        else:
            res = fn(text)
    except Exception as e:
        # bubble typed exceptions so caller can fallback
        raise

    # Normalize result to str or None
    if res is None:
        return None
    if isinstance(res, str):
        return res
    # If adapter returns dict-like or object, try sensible fields
    try:
        # common shape: { "simplified_text": "..."} or {"text": "..."}
        if isinstance(res, dict):
            return res.get("simplified_text") or res.get("text") or res.get("extracted_text")
        # else stringify fallback
        return str(res)
    except Exception:
        return None


class TextSimplifier:
    def __init__(self, gemini_adapter=None, openrouter_adapter=None, openai_adapter=None):
        """
        You can pass adapter instances if you have them, otherwise the wrapper will
        try to import and instantiate the adapters lazily when needed.
        """
        self._gemini = gemini_adapter
        self._openrouter = openrouter_adapter
        self._openai = openai_adapter

    def _get_gemini(self):
        if self._gemini is None:
            try:
                from services.gemini_api import TextSimplifier as GeminiSimplifier
                self._gemini = GeminiSimplifier()
            except Exception as e:
                logger.debug("Gemini adapter init failed: %s", e)
                self._gemini = None
        return self._gemini

    def _get_openrouter(self):
        if self._openrouter is None:
            try:
                from services.openrouter_api import TextSimplifier as OpenRouterSimplifier
                self._openrouter = OpenRouterSimplifier()
            except Exception as e:
                logger.debug("OpenRouter adapter init failed: %s", e)
                self._openrouter = None
        return self._openrouter

    def _get_openai(self):
        if self._openai is None:
            try:
                from services.openai_api import OpenAISimplifier
                self._openai = OpenAISimplifier()
            except Exception as e:
                logger.debug("OpenAI adapter init failed: %s", e)
                self._openai = None
        return self._openai

    def simplify(self, text: str, level: str = "layman", provider: str = "auto") -> str:
        """
        Simplify `text` for `level`. `provider` can be:
          - "gemini", "openrouter", "openai" (explicit)
          - "auto" or None -> try Gemini -> OpenRouter -> OpenAI
        Returns final simplified string or raises Exception if all fail.
        """
        if not text or not text.strip():
            raise ValueError("Empty text provided to simplifier")

        provider = (provider or "auto").lower()
        tried = []

        # helper to attempt an adapter and return on first success
        def attempt(adapter_getter, name):
            try:
                adapter = adapter_getter()
                if adapter is None:
                    logger.debug("Adapter %s not available", name)
                    tried.append((name, "not-available"))
                    return None
                res = _call_adapter(adapter, text, level)
                if res and str(res).strip():
                    tried.append((name, "ok"))
                    return res
                else:
                    tried.append((name, "empty"))
                    return None
            except RateLimitError as e:
                logger.warning("%s rate-limited: %s", name, e)
                tried.append((name, "rate-limited"))
                return None
            except (APIError, NetworkError, ProviderError) as e:
                logger.exception("%s provider error: %s", name, e)
                tried.append((name, f"error:{type(e).__name__}"))
                return None
            except Exception as e:
                logger.exception("%s unexpected error: %s", name, e)
                tried.append((name, f"unexpected:{type(e).__name__}"))
                return None

        # explicit provider
        if provider in ("gemini",):
            out = attempt(self._get_gemini, "gemini")
            if out: return out
            # fallback chain
            out = attempt(self._get_openrouter, "openrouter")
            if out: return out
            out = attempt(self._get_openai, "openai")
            if out: return out

        elif provider in ("openrouter", "open_route", "open-router"):
            out = attempt(self._get_openrouter, "openrouter")
            if out: return out
            out = attempt(self._get_openai, "openai")
            if out: return out

        elif provider in ("openai", "open-ai"):
            out = attempt(self._get_openai, "openai")
            if out: return out

        else:
            # default auto
            out = attempt(self._get_gemini, "gemini")
            if out: return out
            out = attempt(self._get_openrouter, "openrouter")
            if out: return out
            out = attempt(self._get_openai, "openai")
            if out: return out

        # all failed
        logger.error("All providers failed. Tried: %s", tried)
        raise RuntimeError(f"All simplifier providers failed. Tried: {tried}")

# convenience top-level function
_default_simplifier = TextSimplifier()

def simplify_text(text: str, provider: str = "auto", level: str = "layman") -> str:
    return _default_simplifier.simplify(text, level=level, provider=provider)
