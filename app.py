from flask import Flask
from flask_cors import CORS
from routes.api import api_bp
from config.config import Config

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