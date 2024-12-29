from flask import jsonify, request, send_file, Blueprint
import datetime
import os
from pathlib import Path
from models.models import Entry
from database import data_manager  # We'll create this instance in app.py
import uuid
import pandas as pd

# Create the blueprint here instead
api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/test', methods=['GET'])
def test():
    return jsonify({
        "message": "Test route working helooo",
        "service": "API Routes Module",
        "timestamp": datetime.datetime.now().isoformat()
    }) 

@api.route('/createuserentry', methods=['POST'])
def create_user_entry():
    data = request.get_json()
    
    user_input = data.get('entry')
    if user_input is None or user_input == "":
        return jsonify({"message": "bloop: no data provided"}), 400
    
    #Create new Entry object
    #Note: You'll need to get these IDs from the request or session in real use
    new_entry = Entry(
        id=str(uuid.uuid4()),
        user_id=data.get('user_id'),  # You'll need to send this from frontend
        game_id=data.get('game_id'),  # You'll need to send this from frontend
        card_id=data.get('card_id'),  # You'll need to send this from frontend
        entry_text=user_input,
        created_at=datetime.datetime.now()
    )
    
    #Save entry using DataManager
    data_manager.save_entry(new_entry)
    
    response = {
        "message": "Entry saved: " + user_input,
        "entry_id": "TODO", #,
        "timestamp": "TODO", #new_entry.created_at.isoformat()
    }
    return jsonify(response), 201

@api.route('/cards/<path:filename>')
def serve_card(filename):
    """Serve individual card images"""
    cards_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'dixit cards')
    return send_file(os.path.join(cards_directory, filename))

@api.route('/cards')
def get_card_urls():
    """Get list of all cards with their complete information"""
    cards_df = pd.read_csv(data_manager.files['cards'])
    cards_list = cards_df.to_dict('records')
    return jsonify(cards_list)

