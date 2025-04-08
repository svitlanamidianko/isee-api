from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from typing import List, Dict, Any, Optional
import uuid
from dotenv import load_dotenv
import json
import logging

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    def __init__(self):
        self.creds = None
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        self.setup_credentials()
        
    def setup_credentials(self):
        """Set up Google Sheets credentials"""
        try:
            # First try environment variable
            creds_json = os.getenv('GOOGLE_CREDENTIALS')
            if creds_json:
                logger.info("Using credentials from environment variable")
                try:
                    # If it's a string, try to parse it as JSON
                    creds_dict = json.loads(creds_json)
                    self.creds = service_account.Credentials.from_service_account_info(
                        creds_dict,
                        scopes=SCOPES
                    )
                    return
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse GOOGLE_CREDENTIALS as JSON: {e}")
                    raise

            # Fallback to file if environment variable not found
            logger.info("Falling back to credentials.json file")
            if os.path.exists('credentials.json'):
                self.creds = service_account.Credentials.from_service_account_file(
                    'credentials.json',
                    scopes=SCOPES
                )
            else:
                raise FileNotFoundError("No credentials found in environment or credentials.json")
                
        except Exception as e:
            logger.error(f"Error setting up credentials: {e}")
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

    def update_media_paths(self, sheet_name: str = 'media') -> bool:
        """Update media paths to match the correct format and actual filenames"""
        try:
            # Read current data
            service = build('sheets', 'v4', credentials=self.creds)
            sheet = service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f'{sheet_name}!A1:Z'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return True
                
            headers = values[0]
            # Find media_path column index
            path_col_idx = headers.index('media_path')
            
            # Find rows that need path updates
            updates = []
            for row_idx, row in enumerate(values[1:], start=2):  # Start from 2 to account for header
                if len(row) <= path_col_idx:
                    continue
                    
                current_path = row[path_col_idx]
                
                # Extract just the filename if it's a full path
                filename = os.path.basename(current_path)
                
                # Clean up the filename (remove any spaces, special characters)
                clean_filename = filename.replace(' ', '_').lower()
                
                if current_path != clean_filename:
                    updates.append({
                        'range': f'{sheet_name}!{chr(65 + path_col_idx)}{row_idx}',  # Convert column index to letter
                        'values': [[clean_filename]]
                    })
            
            if updates:
                body = {
                    'valueInputOption': 'RAW',
                    'data': updates
                }
                
                result = sheet.values().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body=body
                ).execute()
                
                print(f"Updated {len(updates)} media paths")
                
            return True
            
        except HttpError as err:
            print(f"Error updating media paths: {err}")
            raise

    def normalize_filename(self, filename: str) -> str:
        """Helper function to normalize filenames for consistency"""
        # Remove any directory path if present
        basename = os.path.basename(filename)
        # Convert to lowercase and replace spaces with underscores
        return basename.replace(' ', '_').lower()

    def update_sheet_ids(self, sheet_name: str) -> bool:
        """Command-line interface for updating missing IDs in a sheet"""
        try:
            print(f"Updating missing IDs in {sheet_name} sheet...")
            success = self.update_missing_ids(sheet_name)
            
            if success:
                print("Successfully updated missing IDs!")
            else:
                print("Failed to update IDs. Check the logs for details.")
            
            return success
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return False

def main():
    """Command-line entry point for updating sheet IDs"""
    # Load environment variables
    load_dotenv()
    
    try:
        # Initialize the sheets manager
        manager = GoogleSheetsManager()
        
        # Update missing IDs in the media sheet
        manager.update_sheet_ids('media')
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 