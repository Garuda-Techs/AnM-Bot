import os
import logging
import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    def __init__(self):
        self.gc = None
        self.sheet = None
        self.connect()
    
    def connect(self):
        try:
            # Get credentials from environment variable inside heroku (json)
            credentials_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
            if not credentials_json:
                logger.warning("GOOGLE_CREDENTIALS_JSON not found, Google Sheets disabled")
                self.gc = None
                self.sheet = None
                return

            #parse creds
            import json
            credentials_info = json.loads(credentials_json)
            
            #scope for gsheets
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']

            creds = Credentials.from_service_account_info(credentials_info, scopes=scope)

            self.gc = gspread.authorize(creds)
            
            # Get the spreadsheet ID from env (NOTE: only put ID inside heroku config vars, not whole url
            spreadsheet_id = os.environ.get('GOOGLE_SHEET_ID')
            if not spreadsheet_id:
                logger.warning("GOOGLE_SHEET_ID not found, Google Sheets disabled")
                self.gc = None
                self.sheet = None
                return

            self.sheet = self.gc.open_by_key(spreadsheet_id).sheet1
            
            # Set up headers if sheet is empty
            if not self.sheet.get_all_records():
                self.sheet.update('A1:D1', [['Username', 'Partner_Username', 'ChatId', 'IsAngel']])
                logger.info("Google Sheet initialized with headers")
            
            logger.info("Connected to Google Sheets successfully")
        except Exception as e:
            logger.error(f"Google Sheets connection failed: {e}")
            self.gc = None
            self.sheet = None
    
    def save_players(self, players):
        if not self.sheet:
            logger.error("No Google Sheets connection")
            return "No Google Sheets connection"
        
        try:
            # Clear existing data, leave headers only
            if self.sheet.row_count > 1:
                self.sheet.delete_rows(2, self.sheet.row_count)
            
            #data preprocessing, the blanks shouldnt be called
            data = []
            for username, player in players.items():
                if player.username:
                    partner_username = player.partner.username if (player.partner and player.partner.username) else ""
                    chat_id = player.chat_id or ""
                    is_angel = player.isAngel
                    
                    data.append([username, partner_username, chat_id, is_angel])
            
            # upload data
            if data:
                self.sheet.update(f'A2:D{len(data)+1}', data)
                logger.info(f"Saved {len(data)} players to Google Sheets")
                return f"Saved {len(data)} players to Google Sheets successfully"
            else:
                logger.info("No players to save")
                return "No players to save"
        except Exception as e:
            logger.error(f"Error saving players to Google Sheets: {e}")
            return f"Error saving players to Google Sheets: {e}"
    
    def is_connected(self):
        #checks google sheet connection
        return self.sheet is not None and self.gc is not None
    
    def load_players(self, players):
        if not self.is_connected():
            logger.error("No Google Sheets connection")
            return "No Google Sheets connection"
        
        try:
            records = self.sheet.get_all_records()
            
            if not records:
                logger.info("No players found in Google Sheets")
                return "No players found in Google Sheets"
            
            # Clear existing players
            players.clear()
            
            # Load players from Google Sheets
            for record in records:
                username = record.get('Username', '').strip().lower()
                partner_username = record.get('Partner_Username', '').strip().lower()
                chat_id = record.get('ChatId', '')
                is_angel_value = record.get('IsAngel', False)
                if isinstance(is_angel_value, str):
                    is_angel = is_angel_value.strip().lower() == "true"
                else:
                    is_angel = bool(is_angel_value)
                
                if username:  # Only process if username exists
                    # Create player with all attributes
                    player_obj = players[username]  # creates a new Player object if it doesn't exis
                    player_obj.username = username
                    player_obj.chat_id = int(chat_id) if chat_id else None
                    player_obj.isAngel = is_angel
                    # Store partner username for later setup
                    player_obj.partner_username = partner_username
            
            # Set up partnerships after all players are loaded
            for username, player in players.items():
                if hasattr(player, 'partner_username') and player.partner_username:
                    partner_username = player.partner_username
                    if partner_username in players:
                        players[username].partner = players[partner_username]
                    # Clean up temporary attribute
                    delattr(player, 'partner_username')
            
            logger.info(f"Loaded {len(records)} players from Google Sheets")
            logger.info(f"Players loaded: {list(players.keys())}")
            return f"Loaded {len(records)} players from Google Sheets"
        except Exception as e:
            logger.error(f"Error loading players from Google Sheets: {e}")
            return f"Error loading players from Google Sheets: {e}"

# global Google Sheets manager instance
gs_manager = GoogleSheetsManager()
