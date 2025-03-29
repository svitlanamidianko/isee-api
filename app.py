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


@app.route('/api/collective-view/<game_id>', methods=['GET'])
def get_collective_view(game_id):
    try:
        entries_df = pd.read_csv('data/entries.csv')
        media_df = pd.read_csv('data/media.csv')

        # Group by card_id and create response
        media_data = []
        for media_id in entries_df['media_id'].unique():
            media_entries = entries_df[entries_df['media_id'] == media_id]
            media_info = media_df[media_df['id'] == media_id].iloc[0]
            
            media_data.append({
                'media_id': media_id,
                'media_url': media_info['media_path'],
                'media_name': media_info['media_name'],
                'entries': [{
                    'entry_text': row['entry_text']
                } for _, row in media_entries.iterrows()]
            })
        
        return jsonify({'cards': media_data})
    except Exception as e:
        print(f"Error: {str(e)}")  # Add this line for debugging
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear-entries', methods=['POST'])
def clear_entries():
    try:
        # Read the existing CSV to get the column names
        df = pd.read_csv('data/entries.csv')
        # Create an empty DataFrame with the same columns
        empty_df = pd.DataFrame(columns=df.columns)
        # Save the empty DataFrame back to CSV
        empty_df.to_csv('data/entries.csv', index=False)
        return jsonify({"message": "Entries cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add this route for serving images
@app.route('/api/cards/<path:filename>')
def serve_image(filename):
    try:
        return send_from_directory('assets/dixit cards', filename)
    except Exception as e:
        print(f"Error serving image: {str(e)}")
        return jsonify({'error': 'Image not found'}), 404

# Then register the blueprint
app.register_blueprint(api)


# 6. Run the app (only if this file is run directly)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7777))  # Changed default port to 7777 for local development
    app.run(host='0.0.0.0', port=port)