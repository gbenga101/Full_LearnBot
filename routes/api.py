from flask import Blueprint, request, jsonify
from services.gemini_api import TextSimplifier
from services.flan_api import T5Simplifier

api_bp = Blueprint('api', __name__)
gemini_simplifier = TextSimplifier()
t5_simplifier = T5Simplifier()

@api_bp.route('/')
def home():
    return "Hello, World! Backend is running."

@api_bp.route('/simplify', methods=['POST'])
def simplify():
    data = request.get_json()
    if not data or 'text' not in data or 'level' not in data:
        return jsonify({'error': 'Missing "text" or "level" in request'}), 400

    text = data['text']
    level = data['level']

    simplified = gemini_simplifier.simplify_text(text, level)
    if simplified:
        return jsonify({'simplified_text': simplified}), 200
    else:
        return jsonify({'error': 'Failed to simplify text. Please try again later.'}), 500

@api_bp.route('/simplify/t5', methods=['POST'])
def simplify_with_t5():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing "text" in request'}), 400

    text = data['text']
    level = data.get('level', 'layman')

    simplified = t5_simplifier.simplify(text, level)
    return jsonify({'simplified_text': simplified}), 200
