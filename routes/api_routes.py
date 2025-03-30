from flask import jsonify, request, send_file, Blueprint
import datetime
import os
from pathlib import Path
from models.models import Entry
from database import data_manager  # We'll create this instance in app.py
from database.sheets_manager import GoogleSheetsManager
import uuid
import pandas as pd

# Create the blueprint here instead
api = Blueprint('api', __name__, url_prefix='/api')

# Initialize sheets manager
sheets_manager = GoogleSheetsManager()

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
    cards_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'birthday_cards')
    full_path = os.path.join(cards_directory, filename)
    print(f"Attempting to serve file: {full_path}")
    print(f"File exists: {os.path.exists(full_path)}")
    print(f"Directory contents: {os.listdir(cards_directory)}")
    
    try:
        if os.path.exists(full_path):
            return send_file(full_path)
        else:
            print(f"File not found: {full_path}")
            return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        print(f"Error serving image: {e}")
        return jsonify({'error': 'Image not found'}), 404



@api.route('/cards')
def get_card_urls():
    """Get list of all cards with their complete information"""
    try:
        # Get cards from Google Sheets
        cards_list = sheets_manager.read_sheet('media!A1:F')
        
        # Add the full URL path for each card
        for card in cards_list:
            if 'media_path' in card:
                card['url'] = f"/api/cards/{card['media_path']}"
        
        return jsonify(cards_list)
    except Exception as e:
        print(f"Error getting cards: {e}")
        return jsonify({'error': 'Could not fetch cards'}), 500



@api.route('/collective-view')
def get_collective_view():
    """Get cards with their associated entries"""
    try:
        # Get data from Google Sheets
        entries = sheets_manager.read_sheet('entries!A1:C')
        cards = sheets_manager.read_sheet('media!A1:G')  # Extended to include column G for is_horizontal
        
        # Convert entries to DataFrame if we have any
        entries_df = pd.DataFrame(entries) if entries else pd.DataFrame()
        
        # Create response with all cards
        cards_data = []
        for card in cards:
            # For each card, find its entries if any exist
            card_entries = []
            if not entries_df.empty:
                card_entries = entries_df[entries_df['media_id'] == card['id']]
                card_entries = [{'entry_text': row['entry_text']} for _, row in card_entries.iterrows()]
            
            # Convert is_horizontal to boolean - handle both string and integer values
            is_horizontal = card.get('is_horizontal', False)
            if isinstance(is_horizontal, str):
                is_horizontal = is_horizontal.lower() in ['1', 'true', 'yes']
            elif isinstance(is_horizontal, (int, float)):
                is_horizontal = bool(int(is_horizontal))
            else:
                is_horizontal = bool(is_horizontal)
            
            cards_data.append({
                'card_id': card['id'],
                'card_url': f"/api/cards/{card['media_path']}",
                'card_name': card['media_name'],
                'text': card.get('text', ''),  # Include card text if it exists
                'linkie': card.get('linkie', ''),  # Include link if it exists
                'order': card.get('order', ''),  # Include order if it exists
                'is_horizontal': is_horizontal,  # Now properly converted to boolean
                'entries': card_entries
            })
        
        # Sort by order if it exists
        cards_data.sort(key=lambda x: int(x['order']) if x['order'] else float('inf'))
        
        return jsonify({'cards': cards_data})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

