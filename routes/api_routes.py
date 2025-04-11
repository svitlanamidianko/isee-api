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

@api.route('/createentry', methods=['POST'])
def create_entry():
    data = request.get_json()
    
    # Get the required fields
    entry_text = data.get('entry_text')
    media_id = data.get('media_id')
    
    # Validate input
    if not entry_text or not media_id:
        return jsonify({
            "error": "Missing required fields. Please provide both entry_text and media_id"
        }), 400
    
    # Generate a unique ID (using first 8 characters of UUID)
    entry_id = str(uuid.uuid4())[:8]
    
    # Prepare the entry data as a list
    entry_data = [entry_id, media_id, entry_text]
    
    try:
        # Write to the entries sheet using append_row (not append_rows)
        sheets_manager.append_row('entries!A:C', entry_data)
        
        response = {
            "message": "Entry saved successfully",
            "entry_id": entry_id,
            "media_id": media_id,
            "entry_text": entry_text,
            "timestamp": datetime.datetime.now().isoformat()
        }
        return jsonify(response), 201
        
    except Exception as e:
        print(f"Error saving entry: {e}")
        return jsonify({"error": "Failed to save entry"}), 500

@api.route('/cards/<path:filename>')
def serve_card(filename):
    """Serve individual card images"""
    cards_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'birthday_cards')
    full_path = os.path.join(cards_directory, filename)

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

@api.route('/story-view')
def get_story_view():
    """Get cards with their associated entries"""
    try:
        # Get data from Google Sheets
        entries = sheets_manager.read_sheet('entries!A1:C')
        cards = sheets_manager.read_sheet('media!A1:G')  # Extended to include column G for is_horizontal
        
        # Create response with all cards
        cards_data = []
        
        # Create DataFrame directly from the entries list of dictionaries
        entries_df = None
        if entries:
            try:
                entries_df = pd.DataFrame(entries)
            except Exception as df_error:
                print(f"Error creating DataFrame: {df_error}")
                entries_df = None
        
        for card in cards:
            # Skip if card doesn't have required fields
            if 'id' not in card or 'media_path' not in card:
                continue
                
            # For each card, find its entries if any exist
            card_entries = []
            if entries_df is not None:
                try:
                    matching_entries = entries_df[entries_df['media_id'] == card['id']]
                    card_entries = [{'entry_text': row['entry_text']} 
                                  for _, row in matching_entries.iterrows() 
                                  if 'entry_text' in row]
                except Exception as entry_error:
                    print(f"Error processing entries for card {card['id']}: {entry_error}")
                    card_entries = []
            
            # Convert is_horizontal to boolean - handle both string and integer values
            try:
                is_horizontal = card.get('is_horizontal', False)
                if isinstance(is_horizontal, str):
                    is_horizontal = is_horizontal.lower() in ['1', 'true', 'yes']
                elif isinstance(is_horizontal, (int, float)):
                    is_horizontal = bool(int(is_horizontal))
                else:
                    is_horizontal = bool(is_horizontal)
            except Exception:
                is_horizontal = False
            
            card_data = {
                'card_id': card['id'],
                'card_url': f"/api/cards/{card['media_path']}",
                'card_name': card.get('media_name', ''),
                'text': card.get('text', ''),
                'linkie': card.get('linkie', ''),
                'order': card.get('order', ''),
                'is_horizontal': is_horizontal,
                'entries': card_entries
            }
            cards_data.append(card_data)
        
        # Sort by order if it exists, with error handling
        try:
            cards_data.sort(key=lambda x: int(x['order']) if x['order'] and x['order'].isdigit() else float('inf'))
        except Exception as sort_error:
            print(f"Error sorting cards: {sort_error}")
        
        return jsonify({'cards': cards_data})
    except Exception as e:
        print(f"Error in get_story_view: {str(e)}")
        return jsonify({'error': str(e)}), 500

