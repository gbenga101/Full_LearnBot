# routes/api.py
import logging
from flask import Blueprint, request, jsonify
import hashlib, os, time

from services.openai_api import OpenAISimplifier
from services.openrouter_api import TextSimplifier as OpenRouterSimplifier
from services.exceptions import RateLimitError, APIError, NetworkError, ProviderError
from services.validator import validate_and_format

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

openai_simplifier = OpenAISimplifier()

openrouter_simplifier = None
try:
    openrouter_simplifier = OpenRouterSimplifier()
except Exception as e:
    logger.exception("Failed to init OpenRouterSimplifier (will try fallback chain without it): %s", e)

simple_cache = {}
CACHE_MAX_ITEMS = 512
CACHE_TTL_SECONDS = 60 * 60  # 1 hour

def make_cache_key(provider: str, level: str, text: str) -> str:
    key_source = f"{provider}|{level}|{text}"
    return hashlib.sha256(key_source.encode()).hexdigest()

def get_cached(key: str):
    entry = simple_cache.get(key)
    if not entry:
        return None
    if time.time() - entry.get("ts", 0) > CACHE_TTL_SECONDS:
        try:
            del simple_cache[key]
        except KeyError:
            pass
        return None
    return entry.get("result")

def set_cached(key: str, value: str):
    if len(simple_cache) >= CACHE_MAX_ITEMS:
        first_key = next(iter(simple_cache))
        try:
            del simple_cache[first_key]
        except KeyError:
            pass
    simple_cache[key] = {"result": value, "ts": time.time()}

# lazy loaders for optional heavy providers (local T5 kept)
def get_t5_simplifier():
    try:
        from services.flan_api import T5Simplifier
        return T5Simplifier()
    except Exception as e:
        logger.exception("Failed to import/init local T5Simplifier: %s", e)
        return None

def get_gemini_simplifier():
    try:
        from services.gemini_api import TextSimplifier
        return TextSimplifier()
    except Exception as e:
        logger.exception("Failed to import/init Gemini TextSimplifier: %s", e)
        return None

@api_bp.route('/')
def home():
    return "✅ LearnBot API is running.", 200

@api_bp.route('/simplify', methods=['POST'])
def simplify():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON payload found'}), 400

        text = (data.get('text') or "").strip()
        level = data.get('level', 'layman')
        provider = (data.get('provider') or 'gemini').lower()

        if not text:
            return jsonify({'error': 'Missing required field: "text"'}), 400

        # Check cache first
        cache_key = make_cache_key(provider, level, text)
        cached = get_cached(cache_key)
        if cached:
            logger.info("Cache hit for key %s (provider=%s)", cache_key, provider)
            return jsonify({'simplified_text': cached, 'cached': True}), 200

        simplified = None

        # Helper: safe OpenAI call
        def call_openai(text, level):
            try:
                res = openai_simplifier.simplify(text, level)
            except Exception as e:
                logger.exception("OpenAI call raised an exception: %s", e)
                return None
            if isinstance(res, str) and res.startswith("⚠️"):
                return None
            return res

        # Helper: wrap into structure if needed
        def enforce_structure(raw_text: str) -> str:
            if not raw_text:
                return None
            try:
                return validate_and_format(raw_text)
            except Exception:
                pass
            return (
                "### Simple Explanation\n"
                f"{raw_text.strip()}\n\n"
                "### Key Points\n"
                "- (Raw output, no structured bullets available)"
            )

        # --- Provider flows ---
        if provider == 'openai':
            logger.info("Provider chosen: OpenAI (user-selected).")
            res = call_openai(text, level)
            if res:
                simplified = res

        elif provider == 't5':
            logger.info("Provider chosen: T5 (user-selected).")
            local_t5 = get_t5_simplifier()
            if local_t5:
                try:
                    simplified = local_t5.simplify(text, level)
                except Exception as e:
                    logger.exception("❌ Local T5 crashed: %s", e)

            if not simplified:
                gemini = get_gemini_simplifier()
                if gemini:
                    try:
                        simplified = gemini.simplify_text(text, level)
                    except RateLimitError:
                        logger.warning("Gemini rate-limited; trying OpenRouter/OpenAI.")
                    except ProviderError as e:
                        logger.exception("Gemini provider error: %s", e)

            if not simplified and openrouter_simplifier:
                try:
                    simplified = openrouter_simplifier.simplify_text(text, level)
                except RateLimitError:
                    logger.warning("OpenRouter rate-limited; trying OpenAI.")
                except ProviderError as e:
                    logger.exception("OpenRouter provider error: %s", e)

            if not simplified:
                simplified = call_openai(text, level)

        else:
            # default = Gemini flow
            logger.info("Provider chosen: Gemini (default).")
            gemini = get_gemini_simplifier()
            if gemini:
                try:
                    simplified = gemini.simplify_text(text, level)
                except RateLimitError:
                    logger.warning("Gemini rate-limited; trying OpenRouter.")
                except ProviderError as e:
                    logger.exception("Gemini provider error: %s", e)

            if not simplified:
                logger.info("Falling back to OpenRouter.")
                if openrouter_simplifier:
                    try:
                        simplified = openrouter_simplifier.simplify_text(text, level)
                    except RateLimitError:
                        logger.warning("OpenRouter rate-limited; trying OpenAI.")
                    except ProviderError as e:
                        logger.exception("OpenRouter provider error: %s", e)

            if not simplified:
                logger.info("Falling back to OpenAI.")
                simplified = call_openai(text, level)

        # --- Always enforce structure ---
        final_text = enforce_structure(simplified)

        if final_text:
            set_cached(cache_key, final_text)
            return jsonify({
                'simplified_text': final_text,
                'evidence': None,
                'provider': provider,
                'fallback_chain': ['gemini', 'openrouter', 'openai'],
                'cached': False
            }), 200

        logger.error("All providers failed (provider=%s).", provider)
        return jsonify({'error': 'All providers failed to simplify text.'}), 500

    except Exception as e:
        logger.exception("Unexpected server error in /simplify")
        return jsonify({'error': f'Unexpected server error: {str(e)}'}), 500