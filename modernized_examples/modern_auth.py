"""
Modern Google Authentication for Kairos
Replaces deprecated oauth2client with google-auth
Provides secure, maintained authentication for Google Sheets integration
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google.auth.transport.requests import Request
import gspread
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class ModernGoogleAuth:
    """
    Modern Google authentication manager
    Replaces deprecated oauth2client with google-auth
    """
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/gmail.readonly'  # For email processing
    ]
    
    def __init__(self, credentials_path: str, token_path: Optional[str] = None):
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path) if token_path else None
        self.logger = logging.getLogger(__name__)
        self._credentials: Optional[Credentials] = None
        
    def get_credentials(self) -> Credentials:
        """
        Get valid credentials, refreshing if necessary
        
        Returns:
            Valid Google credentials
            
        Raises:
            FileNotFoundError: If credentials file not found
            ValueError: If credentials are invalid
        """
        if self._credentials and self._credentials.valid:
            return self._credentials
            
        if self._credentials and self._credentials.expired and self._credentials.refresh_token:
            try:
                self._credentials.refresh(Request())
                self._save_token()
                return self._credentials
            except RefreshError as e:
                self.logger.warning(f"Failed to refresh credentials: {e}")
                
        # Load new credentials
        self._credentials = self._load_credentials()
        return self._credentials
    
    def _load_credentials(self) -> Credentials:
        """Load credentials from file"""
        if not self.credentials_path.exists():
            raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
            
        try:
            with open(self.credentials_path, 'r') as f:
                cred_data = json.load(f)
                
            # Check if it's a service account file
            if 'type' in cred_data and cred_data['type'] == 'service_account':
                return ServiceAccountCredentials.from_service_account_file(
                    self.credentials_path, scopes=self.SCOPES
                )
            else:
                # OAuth2 credentials
                return self._load_oauth_credentials(cred_data)
                
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid credentials file format: {e}")
    
    def _load_oauth_credentials(self, cred_data: Dict[str, Any]) -> Credentials:
        """Load OAuth2 credentials"""
        # Load existing token if available
        token_data = {}
        if self.token_path and self.token_path.exists():
            try:
                with open(self.token_path, 'r') as f:
                    token_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        credentials = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            id_token=token_data.get('id_token'),
            token_uri=cred_data.get('token_uri'),
            client_id=cred_data.get('client_id'),
            client_secret=cred_data.get('client_secret'),
            scopes=self.SCOPES
        )
        
        # Refresh if needed
        if not credentials.valid and credentials.refresh_token:
            credentials.refresh(Request())
            self._save_token()
            
        return credentials
    
    def _save_token(self) -> None:
        """Save token for future use"""
        if not self.token_path or not self._credentials:
            return
            
        token_data = {
            'token': self._credentials.token,
            'refresh_token': self._credentials.refresh_token,
            'id_token': self._credentials.id_token,
            'token_uri': self._credentials.token_uri,
            'client_id': self._credentials.client_id,
            'client_secret': self._credentials.client_secret,
            'scopes': self._credentials.scopes
        }
        
        try:
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, 'w') as f:
                json.dump(token_data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save token: {e}")


class ModernSheetsExporter:
    """
    Modern Google Sheets exporter using updated authentication
    Replaces the old Google Sheets integration in mail.py
    """
    
    def __init__(self, auth_manager: ModernGoogleAuth):
        self.auth = auth_manager
        self.logger = logging.getLogger(__name__)
        self._client: Optional[gspread.Client] = None
        
    def get_client(self) -> gspread.Client:
        """Get authenticated gspread client"""
        if not self._client:
            credentials = self.auth.get_credentials()
            self._client = gspread.authorize(credentials)
        return self._client
    
    def export_signals(
        self, 
        spreadsheet_name: str, 
        worksheet_name: str,
        data: List[Dict[str, Any]],
        start_row: int = 2
    ) -> bool:
        """
        Export signals to Google Sheets
        
        Args:
            spreadsheet_name: Name of the spreadsheet
            worksheet_name: Name of the worksheet
            data: List of signal data dictionaries
            start_row: Starting row number (1-indexed)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = self.get_client()
            spreadsheet = client.open(spreadsheet_name)
            
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=worksheet_name, 
                    rows=1000, 
                    cols=20
                )
                self.logger.info(f"Created new worksheet: {worksheet_name}")
            
            # Prepare data for batch update
            if not data:
                self.logger.warning("No data to export")
                return True
                
            # Convert data to rows
            headers = list(data[0].keys())
            rows = []
            
            # Add headers if starting from row 1
            if start_row == 1:
                rows.append(headers)
                
            # Add data rows
            for item in data:
                row = [str(item.get(header, '')) for header in headers]
                rows.append(row)
            
            # Batch update for better performance
            range_name = f'A{start_row}:Z{start_row + len(rows) - 1}'
            worksheet.update(range_name, rows)
            
            self.logger.info(f"Successfully exported {len(data)} records to {spreadsheet_name}/{worksheet_name}")
            return True
            
        except HttpError as e:
            self.logger.error(f"Google Sheets API error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error exporting to sheets: {e}")
            return False
    
    def create_watchlist_sheet(
        self, 
        spreadsheet_name: str, 
        symbols: List[str],
        timestamp: str
    ) -> bool:
        """Create a new worksheet with watchlist symbols"""
        try:
            client = self.get_client()
            spreadsheet = client.open(spreadsheet_name)
            
            worksheet_name = f"Watchlist_{timestamp}"
            worksheet = spreadsheet.add_worksheet(
                title=worksheet_name, 
                rows=len(symbols) + 10, 
                cols=5
            )
            
            # Add headers
            headers = ['Symbol', 'Exchange', 'Added', 'Status', 'Notes']
            worksheet.update('A1:E1', [headers])
            
            # Add symbols
            symbol_data = []
            for symbol in symbols:
                if ':' in symbol:
                    exchange, ticker = symbol.split(':', 1)
                else:
                    exchange, ticker = '', symbol
                    
                symbol_data.append([ticker, exchange, timestamp, 'Active', ''])
            
            if symbol_data:
                range_name = f'A2:E{len(symbol_data) + 1}'
                worksheet.update(range_name, symbol_data)
            
            self.logger.info(f"Created watchlist sheet: {worksheet_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating watchlist sheet: {e}")
            return False


# Example usage and migration guide
def migrate_from_oauth2client():
    """
    Migration guide from oauth2client to google-auth
    
    OLD CODE (oauth2client - DEPRECATED):
    from oauth2client.service_account import ServiceAccountCredentials
    
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    
    NEW CODE (google-auth - MODERN):
    """
    
    # Initialize modern auth
    auth_manager = ModernGoogleAuth(
        credentials_path='credentials.json',
        token_path='token.json'  # Optional for OAuth2 flows
    )
    
    # Create sheets exporter
    sheets_exporter = ModernSheetsExporter(auth_manager)
    
    # Export data (same interface, modern backend)
    sample_data = [
        {'symbol': 'AAPL', 'signal': 'BUY', 'price': 150.00},
        {'symbol': 'GOOGL', 'signal': 'SELL', 'price': 2500.00}
    ]
    
    success = sheets_exporter.export_signals(
        spreadsheet_name='Trading Signals',
        worksheet_name='Alerts',
        data=sample_data
    )
    
    return success


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    try:
        result = migrate_from_oauth2client()
        print(f"Migration test: {'SUCCESS' if result else 'FAILED'}")
    except Exception as e:
        print(f"Migration test failed: {e}")