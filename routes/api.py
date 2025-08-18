from flask import Blueprint, request, jsonify
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