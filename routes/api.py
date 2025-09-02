# routes/api.py
import logging
from flask import Blueprint, request, jsonify
import hashlib, os, time

# light-weight imports (these should not import heavy ML libs)
from services.openai_api import OpenAISimplifier
from services.hf_api import HFSimplifier

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# instantiate light/always-available services
openai_simplifier = OpenAISimplifier()
hf_simplifier = HFSimplifier()  # uses HF API (hosted)

# Simple in-memory cache for demo (not persistent; ok for showcase)
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

# helpers to lazy-load heavy providers
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

        def is_failure(resp):
            return not resp or (isinstance(resp, str) and resp.startswith("⚠️"))

        # Check cache first
        cache_key = make_cache_key(provider, level, text)
        cached = get_cached(cache_key)
        if cached:
            logger.info("Cache hit for key %s (provider=%s)", cache_key, provider)
            return jsonify({'simplified_text': cached, 'cached': True}), 200

        simplified = None

        # OpenAI chosen: only OpenAI
        if provider == 'openai':
            logger.info("Provider chosen: OpenAI (user-selected). Calling OpenAI only.")
            simplified = openai_simplifier.simplify(text, level)
            if is_failure(simplified):
                logger.info("OpenAI returned an error-like response for the request.")

        # T5 chosen: try hosted HF first, then local T5, then Gemini, then OpenAI
        elif provider == 't5':
            logger.info("Provider chosen: T5 (user-selected). Trying hosted HF first.")
            try:
                simplified = hf_simplifier.simplify(text, level)
            except Exception as e:
                logger.exception("❌ HF hosted call crashed: %s", e)
                simplified = "⚠️ HF error"

            if is_failure(simplified):
                logger.warning("Hosted HF failed or returned error. Attempting local T5.")
                local_t5 = get_t5_simplifier()
                if local_t5:
                    try:
                        simplified = local_t5.simplify(text, level)
                    except Exception as e:
                        logger.exception("❌ Local T5 crashed: %s", e)
                        simplified = "⚠️ Local T5 error"
                if is_failure(simplified):
                    logger.warning("Local T5 failed or missing. Falling back to Gemini -> OpenAI.")
                    gemini = get_gemini_simplifier()
                    if gemini:
                        try:
                            simplified = gemini.simplify_text(text, level)
                        except Exception as e:
                            logger.exception("❌ Gemini crashed: %s", e)
                            simplified = "⚠️ Gemini error"
                    if is_failure(simplified):
                        simplified = openai_simplifier.simplify(text, level)

        # Default / Gemini: try Gemini, then hosted HF, then OpenAI
        else:
            logger.info("Provider chosen: Gemini (default). Trying Gemini first.")
            gemini = get_gemini_simplifier()
            if gemini:
                try:
                    simplified = gemini.simplify_text(text, level)
                except Exception as e:
                    logger.exception("❌ Gemini crashed: %s", e)
                    simplified = "⚠️ Gemini error"
            else:
                logger.warning("Gemini service unavailable (suspended or import failed).")

            if is_failure(simplified):
                logger.warning("Gemini failed or returned invalid result. Falling back to hosted HF.")
                try:
                    simplified = hf_simplifier.simplify(text, level)
                except Exception as e:
                    logger.exception("❌ HF hosted call crashed: %s", e)
                    simplified = "⚠️ HF error"
                if is_failure(simplified):
                    logger.warning("Hosted HF failed. Falling back to OpenAI.")
                    simplified = openai_simplifier.simplify(text, level)

        # cache successful responses (non-failure)
        if simplified and not is_failure(simplified):
            set_cached(cache_key, simplified)

        if simplified and not (isinstance(simplified, str) and simplified == ""):
            return jsonify({'simplified_text': simplified, 'cached': False}), 200
        else:
            logger.error("All providers failed to produce a valid simplification for this request (provider=%s).", provider)
            return jsonify({'error': 'All providers failed to simplify text.'}), 500

    except Exception as e:
        logger.exception("Unexpected server error in /simplify")
        return jsonify({'error': f'Unexpected server error: {str(e)}'}), 500


#FALLBACK WHEN ERROR CODE (MUST)
""" # routes/api.py
import logging
from flask import Blueprint, request, jsonify
from services.gemini_api import TextSimplifier
from services.flan_api import T5Simplifier
from services.openai_api import OpenAISimplifier

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Instantiate services once
gemini_simplifier = TextSimplifier()
t5_simplifier = T5Simplifier()
openai_simplifier = OpenAISimplifier()

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

        # Helper to detect failure from service responses
        def is_failure(resp):
            return not resp or (isinstance(resp, str) and resp.startswith("⚠️"))

        simplified = None

        # --- OpenAI selected: only OpenAI, no fallback ---
        if provider == 'openai':
            logger.info("Provider chosen: OpenAI (user-selected). Calling OpenAI only.")
            simplified = openai_simplifier.simplify(text, level)
            # If OpenAI returns an error-like string (starts with ⚠️), still return it to user but log it
            if is_failure(simplified):
                logger.info("OpenAI returned an error-like response for the request.")

        # --- T5 selected: T5 -> Gemini -> OpenAI ---
        elif provider == 't5':
            logger.info("Provider chosen: T5 (user-selected). Trying T5 first.")
            simplified = t5_simplifier.simplify(text, level)

            if is_failure(simplified):
                logger.warning("T5 failed or returned invalid result. Falling back to Gemini.")
                simplified = gemini_simplifier.simplify_text(text, level)

                if is_failure(simplified):
                    logger.warning("Gemini also failed. Falling back to OpenAI.")
                    simplified = openai_simplifier.simplify(text, level)

        # --- Default / Gemini selected: Gemini -> T5 -> OpenAI ---
        else:
            logger.info("Provider chosen: Gemini (default). Trying Gemini first.")
            simplified = gemini_simplifier.simplify_text(text, level)

            if is_failure(simplified):
                logger.warning("Gemini failed or returned invalid result. Falling back to T5.")
                simplified = t5_simplifier.simplify(text, level)

                if is_failure(simplified):
                    logger.warning("T5 also failed. Falling back to OpenAI.")
                    simplified = openai_simplifier.simplify(text, level)

        # Final response handling
        if simplified and not (isinstance(simplified, str) and simplified == ""):
            return jsonify({'simplified_text': simplified}), 200
        else:
            logger.error("All providers failed to produce a valid simplification for this request (provider=%s).", provider)
            return jsonify({'error': 'All providers failed to simplify text.'}), 500

    except Exception as e:
        logger.exception("Unexpected server error in /simplify")
        return jsonify({'error': f'Unexpected server error: {str(e)}'}), 500 """

# PREVIOUS WORKING CODE

""" from flask import Blueprint, request, jsonify
from services.gemini_api import TextSimplifier
from services.flan_api import T5Simplifier
from services.openai_api import OpenAISimplifier   # ✅ new import

api_bp = Blueprint('api', __name__)

# Instantiate simplifiers once
gemini_simplifier = TextSimplifier()
t5_simplifier = T5Simplifier()
openai_simplifier = OpenAISimplifier()   # ✅ new instance

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
            return jsonify({'error': 'Missing required field: \"text\"'}), 400

        simplified = None

        if provider == 't5':
            simplified = t5_simplifier.simplify(text, level)

        elif provider == 'openai':   # ✅ allow explicit OpenAI choice
            simplified = openai_simplifier.simplify(text, level)

        else:  # default → Gemini
            simplified = gemini_simplifier.simplify_text(text, level)
            # ✅ Fallback to OpenAI if Gemini fails
            if not simplified or simplified.startswith("⚠️"):
                simplified = openai_simplifier.simplify(text, level)

        if simplified:
            return jsonify({'simplified_text': simplified}), 200
        else:
            return jsonify({'error': f'{provider.upper()} failed to simplify text'}), 500

    except Exception as e:
        return jsonify({'error': f'Unexpected server error: {str(e)}'}), 500

 """


# FIRST WORKING CODE
""" from flask import Blueprint, request, jsonify
from services.gemini_api import TextSimplifier
from services.flan_api import T5Simplifier

api_bp = Blueprint('api', __name__)

# Instantiate both simplifiers
gemini_simplifier = TextSimplifier()
t5_simplifier = T5Simplifier()


@api_bp.route('/')
def home():
    return "✅ LearnBot API is running.", 200
@api_bp.route('/simplify', methods=['POST'])
def simplify_with_gemini():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON payload found'}), 400

        text = data.get('text')
        level = data.get('level')

        if not text or not level:
            return jsonify({'error': 'Missing required fields: "text" and "level"'}), 400

        simplified = gemini_simplifier.simplify_text(text, level)

        if simplified:
            return jsonify({'simplified_text': simplified}), 200
        else:
            return jsonify({'error': 'Gemini failed to simplify text'}), 500

    except Exception as e:
        return jsonify({'error': f'Unexpected server error: {str(e)}'}), 500

@api_bp.route('/simplify/t5', methods=['POST'])
def simplify_with_t5():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON payload found'}), 400

        text = data.get('text')
        level = data.get('level', 'layman')

        if not text:
            return jsonify({'error': 'Missing required field: "text"'}), 400

        simplified = t5_simplifier.simplify(text, level)

        if simplified:
            return jsonify({'simplified_text': simplified}), 200
        else:
            return jsonify({'error': 'T5 failed to simplify text'}), 500

    except Exception as e:
        return jsonify({'error': f'Unexpected server error: {str(e)}'}), 500 """



""" PREVIOUS WORKING CODE (DON'T DELETE, USE FOR FALLBACK) """
""" from flask import Blueprint, request, jsonify
from services.gemini_api import TextSimplifier
from services.flan_api import T5Simplifier

api_bp = Blueprint('api', __name__)

# Instantiate both simplifiers once
gemini_simplifier = TextSimplifier()
t5_simplifier = T5Simplifier()

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

        if provider == 't5':
            simplified = t5_simplifier.simplify(text, level)
        else:
            # default -> gemini
            simplified = gemini_simplifier.simplify_text(text, level)

        if simplified:
            return jsonify({'simplified_text': simplified}), 200
        else:
            return jsonify({'error': f'{provider.upper()} failed to simplify text'}), 500

    except Exception as e:
        # keep error response generic; server logs will have details
        return jsonify({'error': f'Unexpected server error: {str(e)}'}), 500 """