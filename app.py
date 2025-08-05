from flask import Flask
from flask_cors import CORS
from routes.api import api_bp
from config.config import Config

app = Flask(__name__)
# Enable CORS for all routes
CORS(app, origins=[
    "https://gbenga101.github.io/LearnBot",      # GitHub
    "https://learnbot-now.vercel.app/",  # Vercel frontend domain
    "http://localhost:5500",            # XAMPP and local testing
    "http://127.0.0.1:5500"
])

app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['JSON_SORT_KEYS'] = False # Prevent sorting JSON keys

app.register_blueprint(api_bp)

""" if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(host='0.0.0.0', port=port)
    app.run(debug=debug_mode) """

if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    port = int(os.environ.get('PORT', 5000))  # ✅ Get the dynamic port for Render
    app.run(host='0.0.0.0', port=port, debug=debug_mode)