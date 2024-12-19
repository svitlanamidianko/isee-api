from models.models import Entry
import os
import pandas as pd
import datetime
from typing import List


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
 