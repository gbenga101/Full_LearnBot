from flask import Flask
from routes.api import api_bp

app = Flask(__name__)
app.register_blueprint(api_bp)

import os

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(debug=debug_mode)