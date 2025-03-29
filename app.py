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

load_dotenv()  # Load environment variables from .env file

# 1. Create the Flask app
app = Flask(__name__)

CORS(app)  

# 2. Configure the app
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') 
    DEBUG =  os.environ.get('DEBUG') 

app.config.from_object(Config)

# 3. Set up your data management
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# 4. Define your routes
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the API",
        "version": "1.0.2",
        "status": "running", 
        "timestamp": datetime.datetime.now().isoformat()
    })


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "error": "Resource not found",
        "status_code": 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "status_code": 500
    }), 500

@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({
        "error": "Bad request",
        "status_code": 400
    }), 400

# Then register the blueprint
app.register_blueprint(api)

# 6. Run the app (only if this file is run directly)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7777))  # Changed default port to 7777 for local development
    app.run(host='0.0.0.0', port=port, debug=True)