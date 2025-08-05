from flask import Blueprint, request, jsonify
from services.gemini_api import TextSimplifier

api_bp = Blueprint('api', __name__)
simplifier = TextSimplifier()

@api_bp.route('/')
def home():
    return "Hello, World! Backend is running."

@api_bp.route('/simplify', methods=['POST'])
def simplify():
    data = request.get_json()

    # Validate input
    if not data or 'text' not in data or 'level' not in data:
        return jsonify({'error': 'Missing "text" or "level" in request'}), 400

    text = data['text']
    level = data['level']

    simplified = simplifier.simplify_text(text, level)

    if simplified:
        return jsonify({'simplified_text': simplified}), 200
    else:
        return jsonify({'error': 'Failed to simplify text. Please try again later.'}), 500