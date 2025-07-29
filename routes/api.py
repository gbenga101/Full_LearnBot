from flask import Blueprint
# api_bp is the Blueprint for API routes
api_bp = Blueprint('api', __name__)

@api_bp.route('/')
def home():
    return "Hello, World! Backend is running."