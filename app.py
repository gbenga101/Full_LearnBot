from flask import Flask
from flask_cors import CORS
from routes.api import api_bp
from config.config import Config
import logging

logging.basicConfig(level=logging.DEBUG)  #show logs on Render

app = Flask(__name__)

# ✅ Enable CORS with full support for all origins, methods, and headers
CORS(app, resources={r"/*": {"origins": [
    "https://gbenga101.github.io",
    "https://gbenga101.github.io/LearnBot",
    "https://learnbot-now.vercel.app",
    "http://localhost:5500",
    "http://127.0.0.1:5500"
]}}, supports_credentials=True)

# App config
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['JSON_SORT_KEYS'] = False

# Register API routes
app.register_blueprint(api_bp)

# Run the app (supports Render dynamic port)
if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)

""" 
from flask import Flask, request, jsonify
from flask_cors import CORS
from text_simplifier import TextSimplifier   # your existing Gemini wrapper
from openai_simplifier import OpenAISimplifier  # new file below
import os

app = Flask(__name__)
CORS(app)  # allow local dev calls from file:// or other origins

# initialize providers
gemini = TextSimplifier()
openai = OpenAISimplifier()

@app.route("/simplify", methods=["POST"])
def simplify():
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    level = data.get("level", "layman")
    provider = (data.get("provider") or "gemini").lower()

    if not text:
        return jsonify({"error": "Missing 'text' in request body."}), 400

    try:
        if provider == "openai":
            simplified = openai.simplify_text(text, level)
        else:
            simplified = gemini.simplify_text(text, level)
        return jsonify({"simplified_text": simplified})
    except Exception as e:
        # keep message user-friendly for demo; log full exception in server logs
        app.logger.exception("Error in simplify route")
        return jsonify({"error": "Server error while simplifying. Check server logs."}), 500

if __name__ == "__main__":
    app.run(debug=True) """