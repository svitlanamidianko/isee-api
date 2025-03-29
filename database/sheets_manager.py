from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from typing import List, Dict, Any, Optional
import uuid

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class GoogleSheetsManager:
    def __init__(self):
        self.creds = None
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        self.setup_credentials()
        
    def setup_credentials(self):
        """Set up Google Sheets credentials"""
        try:
            # If using service account (recommended for server applications)
            self.creds = service_account.Credentials.from_service_account_file(
                'credentials.json',
                scopes=SCOPES
            )
        except Exception as e:
            print(f"Error setting up credentials: {e}")
            raise

    def read_sheet(self, range_name: str) -> List[Dict[str, Any]]:
        """Read data from specified range in Google Sheets"""
        try:
            service = build('sheets', 'v4', credentials=self.creds)
            sheet = service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return []
                
            # Convert to list of dictionaries
            headers = values[0]
            return [dict(zip(headers, row)) for row in values[1:]]
            
        except HttpError as err:
            print(f"Error reading from Google Sheets: {err}")
            raise

    def update_sheet(self, range_name: str, values: List[List[Any]]) -> bool:
        """Update data in specified range in Google Sheets"""
        try:
            service = build('sheets', 'v4', credentials=self.creds)
            sheet = service.spreadsheets()
            
            body = {
                'values': values
            }
            
            result = sheet.values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return True
            
        except HttpError as err:
            print(f"Error updating Google Sheets: {err}")
            raise

    def append_row(self, range_name: str, row_data: List[Any]) -> bool:
        """Append a new row to the sheet"""
        try:
            service = build('sheets', 'v4', credentials=self.creds)
            sheet = service.spreadsheets()
            
            body = {
                'values': [row_data]
            }
            
            result = sheet.values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return True
            
        except HttpError as err:
            print(f"Error appending to Google Sheets: {err}")
            raise

    def generate_id(self) -> str:
        """Generate a unique ID"""
        return str(uuid.uuid4())[:8]  # Using first 8 characters of UUID for readability

    def update_missing_ids(self, sheet_name: str) -> bool:
        """Update rows that have missing IDs in the specified sheet"""
        try:
            # Read all data including headers
            service = build('sheets', 'v4', credentials=self.creds)
            sheet = service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{sheet_name}!A1:Z'  # Read all columns
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return True  # Nothing to update
                
            headers = values[0]
            id_column = 0  # Assuming ID is always first column
            
            # Find rows without IDs
            updates = []
            for row_idx, row in enumerate(values[1:], start=2):  # Start from 2 to account for header row
                # If row has no ID (empty or doesn't exist)
                if len(row) == 0 or not row[0]:
                    new_id = self.generate_id()
                    
                    # If row exists but ID is empty
                    if len(row) > 0:
                        row[0] = new_id
                        updates.append({
                            'range': f'{sheet_name}!A{row_idx}',
                            'values': [[new_id]]
                        })
                    else:
                        # If entire row is empty, skip it
                        continue
            
            if updates:
                body = {
                    'valueInputOption': 'RAW',
                    'data': updates
                }
                
                result = sheet.values().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body=body
                ).execute()
                
                print(f"Updated {len(updates)} rows with new IDs")
                
            return True
            
        except HttpError as err:
            print(f"Error updating IDs: {err}")
            raise 