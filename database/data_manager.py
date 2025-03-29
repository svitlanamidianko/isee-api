import pandas as pd
from typing import List, Dict, Any, Optional
from .sheets_manager import GoogleSheetsManager
import os

class DataManager:
    def __init__(self, use_sheets: bool = True):
        self.use_sheets = use_sheets
        if use_sheets:
            self.sheets_manager = GoogleSheetsManager()
        
    def get_media_data(self) -> List[Dict[str, Any]]:
        """Get all media data"""
        if self.use_sheets:
            return self.sheets_manager.read_sheet('media!A1:F')  # Using 'media' sheet
        else:
            df = pd.read_csv('data/media.csv')
            return df.to_dict('records')
            
    def get_entries_data(self) -> List[Dict[str, Any]]:
        """Get all entries data"""
        if self.use_sheets:
            return self.sheets_manager.read_sheet('entries!A1:C')  # Using 'entries' sheet
        else:
            df = pd.read_csv('data/entries.csv')
            return df.to_dict('records')
            
    def update_media_data(self, media_id: int, updates: Dict[str, Any]) -> bool:
        """Update specific media entry"""
        if self.use_sheets:
            # First get current data
            data = self.sheets_manager.read_sheet('media!A1:F')
            # Find the row to update
            row_idx = None
            for idx, row in enumerate(data):
                if str(row.get('id')) == str(media_id):
                    row_idx = idx + 2  # +2 because sheets is 1-indexed and we have header
                    break
                    
            if row_idx is None:
                return False
                
            # Update the row
            range_name = f'media!A{row_idx}:F{row_idx}'
            values = [[
                updates.get('id', data[row_idx-2].get('id')),
                updates.get('order', data[row_idx-2].get('order')),
                updates.get('media_name', data[row_idx-2].get('media_name')),
                updates.get('media_path', data[row_idx-2].get('media_path')),
                updates.get('text', data[row_idx-2].get('text')),
                updates.get('linkie', data[row_idx-2].get('linkie'))
            ]]
            return self.sheets_manager.update_sheet(range_name, values)
        else:
            df = pd.read_csv('data/media.csv')
            mask = df['id'] == media_id
            if not mask.any():
                return False
            for key, value in updates.items():
                df.loc[mask, key] = value
            df.to_csv('data/media.csv', index=False)
            return True
            
    def append_media(self, media_data: Dict[str, Any]) -> bool:
        """Add new media entry"""
        if self.use_sheets:
            values = [
                media_data.get('id', ''),
                media_data.get('order', ''),
                media_data.get('media_name', ''),
                media_data.get('media_path', ''),
                media_data.get('text', ''),
                media_data.get('linkie', '')
            ]
            return self.sheets_manager.append_row('media!A:F', values)
        else:
            df = pd.read_csv('data/media.csv')
            df = df.append(media_data, ignore_index=True)
            df.to_csv('data/media.csv', index=False)
            return True
            
    def append_entry(self, entry_data: Dict[str, Any]) -> bool:
        """Add new entry"""
        if self.use_sheets:
            values = [
                entry_data.get('media_id', ''),
                entry_data.get('entry_text', ''),
                entry_data.get('timestamp', '')
            ]
            return self.sheets_manager.append_row('entries!A:C', values)
        else:
            df = pd.read_csv('data/entries.csv')
            df = df.append(entry_data, ignore_index=True)
            df.to_csv('data/entries.csv', index=False)
            return True 