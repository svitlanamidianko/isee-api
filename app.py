from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
import datetime
from dotenv import load_dotenv
from models.models import User, Deck, Card, Game, Entry, DeckCard
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



@app.route('/api/items', methods=['POST'])
def create_item():
    data = request.get_json()
    df = pd.read_csv(ITEMS_CSV)
    
    # Create new item with auto-incrementing ID
    new_id = 1 if df.empty else df['id'].max() + 1
    new_item = {'id': new_id, 'name': data.get('name')}
    
    df = pd.concat([df, pd.DataFrame([new_item])], ignore_index=True)
    df.to_csv(ITEMS_CSV, index=False)
    
    return jsonify(new_item), 201

@app.route('/api/items/<int:item_id>', methods=['GET']) #api/items/1
def get_item(item_id):
    df = pd.read_csv(ITEMS_CSV)
    item = df[df['id'] == item_id].to_dict('records')
    return jsonify(item[0]) if item else ('Item not found', 404)

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

# Example route using the new models
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = User(
        name=data.get('name'),
        email=data.get('email')
    )
    created_user = data_manager.create_user(user)
    return jsonify(created_user.__dict__), 201

@app.route('/api/collective-view/<game_id>', methods=['GET'])
def get_collective_view(game_id):
    try:
        entries_df = pd.read_csv('data/entries.csv')
        cards_df = pd.read_csv('data/cards.csv')
        
        # Get entries for this game
        game_entries = entries_df[entries_df['game_id'] == game_id]
        
        # Group by card_id and create response
        cards_data = []
        for card_id in game_entries['card_id'].unique():
            card_entries = game_entries[game_entries['card_id'] == card_id]
            card_info = cards_df[cards_df['id'] == card_id].iloc[0]
            
            cards_data.append({
                'card_id': card_id,
                'image_url': card_info['image_path'],
                'name': card_info['name'],
                'entries': [{
                    'entry_text': row['entry_text'],
                    'user_id': row['user_id'],
                    'created_at': row['created_at']
                } for _, row in card_entries.iterrows()]
            })
        
        return jsonify({'cards': cards_data})
    except Exception as e:
        print(f"Error: {str(e)}")  # Add this line for debugging
        return jsonify({'error': str(e)}), 500

# Then register the blueprint
app.register_blueprint(api)

# 6. Run the app (only if this file is run directly)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777, debug=True)