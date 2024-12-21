from models.models import Entry
import os
import pandas as pd
import datetime
from typing import List
import glob
import uuid


class DataManager:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Initialize CSV files
        self.files = {
            'entries': os.path.join(data_dir, 'entries.csv'),
            'users': os.path.join(data_dir, 'users.csv'),
            'games': os.path.join(data_dir, 'games.csv'),
            'cards': os.path.join(data_dir, 'cards.csv')
        }
        
        # Create empty CSVs if they don't exist
        if not os.path.exists(self.files['entries']):
            pd.DataFrame(columns=[
                'id', 'user_id', 'game_id', 'card_id', 
                'entry_text', 'created_at'
            ]).to_csv(self.files['entries'], index=False)
        
        if not os.path.exists(self.files['cards']):
            pd.DataFrame(columns=[
                'id', 'image_path', 'name'
            ]).to_csv(self.files['cards'], index=False)
            # Initialize cards from assets
            self._initialize_cards_from_assets()
    
    def _initialize_cards_from_assets(self):
        """Initialize cards.csv with all Dixit cards from assets directory"""
        cards_df = pd.read_csv(self.files['cards'])
        
        # Get all JPEG files from assets/dixit_cards
        card_files = glob.glob('assets/dixit cards/*.jpeg')
        
        
        new_cards = []
        for card_path in card_files:
            # Extract name from filename (remove path and extension)
            name = os.path.splitext(os.path.basename(card_path))[0]
            
            # Create new card entry
            card_dict = {
                'id': str(uuid.uuid4()),
                'image_path': card_path,
                'name': name
            }
            new_cards.append(card_dict)
        
        # Add new cards to DataFrame
        if new_cards:
            cards_df = pd.concat([cards_df, pd.DataFrame(new_cards)], ignore_index=True)
            cards_df.to_csv(self.files['cards'], index=False)
    
    def save_entry(self, entry: Entry) -> Entry:
        """Save a new entry to the entries.csv file"""
        df = pd.read_csv(self.files['entries'])
        
        # Convert entry to dict for pandas
        entry_dict = {
            'id': entry.id,
            'user_id': entry.user_id,
            'game_id': entry.game_id,
            'card_id': entry.card_id,
            'entry_text': entry.entry_text,
            'created_at': entry.created_at.isoformat()
        }
        
        # Add new entry
        df = pd.concat([df, pd.DataFrame([entry_dict])], ignore_index=True)
        
        # Save back to CSV
        df.to_csv(self.files['entries'], index=False)
        
        return entry
    
    def get_entries_by_game(self, game_id: str) -> List[Entry]:
        """Get all entries for a specific game"""
        df = pd.read_csv(self.files['entries'])
        game_entries = df[df['game_id'] == game_id]
        
        return [
            Entry(
                id=row['id'],
                user_id=row['user_id'],
                game_id=row['game_id'],
                card_id=row['card_id'],
                entry_text=row['entry_text'],
                created_at=datetime.datetime.fromisoformat(row['created_at'])
            )
            for _, row in game_entries.iterrows()
        ]

# Initialize the DataManager
data_manager = DataManager()
 