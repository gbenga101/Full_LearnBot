""" from flask import Flask
from routes.api import api_bp

app = Flask(__name__)
app.register_blueprint(api_bp)

import os

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(debug=debug_mode)

 """
from flask import Flask
from routes.api import api_bp
from config.config import Config

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['JSON_SORT_KEYS'] = False  # Prevent sorting JSON keys

app.register_blueprint(api_bp)

if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(debug=debug_mode)