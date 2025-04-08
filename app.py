from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pandas as pd
import datetime
from dotenv import load_dotenv
from models.models import Media, Entry
from typing import Optional, List
from database import data_manager  # Update this import
from routes.api_routes import api  # This is the correct way to import the Blueprint
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()  # Load environment variables from .env file

# Log all environment variables (excluding sensitive ones)
logger.info("Environment variables:")
for key in os.environ:
    if key not in ['GOOGLE_CREDENTIALS', 'SECRET_KEY']:  # Don't log sensitive values
        logger.info(f"{key}: {os.environ.get(key)}")

# 1. Create the Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://iseebday.vercel.app",
            "http://localhost:3000",  # For local frontend development
            "http://localhost:5000",   # For local backend development
            "http://localhost:5173"    # For Vite/React local development
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# 2. Configure the app
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') 
    DEBUG = os.environ.get('DEBUG') 

app.config.from_object(Config)

# Log configuration
logger.info(f"App Configuration:")
logger.info(f"DEBUG mode: {app.debug}")
logger.info(f"Environment: {os.environ.get('FLASK_ENV')}")
logger.info(f"Port: {os.environ.get('PORT')}")

# 3. Set up your data management
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    logger.info(f"Created data directory: {DATA_DIR}")

# 4. Define your routes
@app.route('/')
def home():
    logger.info("Home endpoint called")
    return jsonify({
        "message": "Welcome to the API",
        "version": "1.0.2",
        "status": "running", 
        "timestamp": datetime.datetime.now().isoformat(),
        "env": os.environ.get('FLASK_ENV', 'unknown'),
        "debug": app.debug,
        "port": os.environ.get('PORT')
    })

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 error: {error}")
    return jsonify({
        "error": "Resource not found",
        "status_code": 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}", exc_info=True)  # Added exc_info for full traceback
    return jsonify({
        "error": "Internal server error",
        "status_code": 500,
        "details": str(error)
    }), 500

@app.errorhandler(400)
def bad_request_error(error):
    logger.error(f"400 error: {error}")
    return jsonify({
        "error": "Bad request",
        "status_code": 400
    }), 400

# Then register the blueprint
logger.info("Registering API blueprint")
app.register_blueprint(api)

# 6. Run the app (only if this file is run directly)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Default to 5000 to match fly.io expectations
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true')