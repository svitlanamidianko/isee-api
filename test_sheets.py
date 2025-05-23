from dotenv import load_dotenv
import os
from database.data_manager import DataManager
from database.sheets_manager import GoogleSheetsManager

# Load environment variables
load_dotenv()

def test_read_media():
    print("Testing reading media data...")
    print(f"Using spreadsheet ID: {os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')}")
    
    dm = DataManager(use_sheets=True)
    try:
        media_data = dm.get_media_data()
        print("\nSuccessfully read media data!")
        print(f"Found {len(media_data)} media entries")
        # Print first entry as example
        if media_data:
            print("\nFirst entry:")
            for key, value in media_data[0].items():
                print(f"{key}: {value}")
    except Exception as e:
        print(f"Error reading media data: {e}")

def test_update_ids():
    print("\nTesting updating missing IDs...")
    sheets_manager = GoogleSheetsManager()
    try:
        # Update IDs in both sheets
        print("Updating 'media' sheet...")
        sheets_manager.update_missing_ids('media')
        print("\nUpdating 'entries' sheet...")
        sheets_manager.update_missing_ids('entries')
        print("\nID updates completed!")
    except Exception as e:
        print(f"Error updating IDs: {e}")

def test_update_paths():
    print("\nTesting updating media paths...")
    sheets_manager = GoogleSheetsManager()
    try:
        print("Updating paths in 'media' sheet...")
        sheets_manager.update_media_paths('media')
        print("\nPath updates completed!")
        
        # Read and show updated data
        data = sheets_manager.read_sheet('media!A1:F')
        print("\nUpdated paths:")
        for row in data:
            if 'media_path' in row:
                print(f"- {row['media_path']}")
    except Exception as e:
        print(f"Error updating paths: {e}")

if __name__ == "__main__":
    test_read_media()
    test_update_ids()
    test_update_paths() 