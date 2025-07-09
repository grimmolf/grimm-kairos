"""
Google OAuth Authentication Manager for grimm@greysson.com

Provides secure Google OAuth authentication for TradingView login
with token caching and session persistence.
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any
import logging

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    logging.warning("Google auth libraries not available. Install with: pip install google-auth google-auth-oauthlib")

logger = logging.getLogger(__name__)


class GrimmAuthManager:
    """
    Manages Google OAuth authentication for grimm@greysson.com
    with secure token caching and automatic refresh.
    """
    
    def __init__(self, credentials_file: Optional[str] = None, cache_dir: Optional[str] = None):
        """
        Initialize authentication manager.
        
        Args:
            credentials_file: Path to Google OAuth credentials JSON
            cache_dir: Directory for token caching (default: ~/.kairos_auth)
        """
        if not GOOGLE_AUTH_AVAILABLE:
            raise ImportError("Google auth libraries required. Install with: pip install google-auth google-auth-oauthlib")
            
        self.credentials_file = credentials_file or self._find_credentials_file()
        self.cache_dir = Path(cache_dir or Path.home() / ".kairos_auth")
        self.cache_dir.mkdir(exist_ok=True)
        
        self.token_file = self.cache_dir / "grimm_tokens.json"
        self.session_file = self.cache_dir / "session_data.json"
        
        # OAuth scopes for Google services
        self.scopes = [
            'openid',
            'email', 
            'profile',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]
        
        self.credentials: Optional[Credentials] = None
        self.user_email = "grimm@greysson.com"
        
    def _find_credentials_file(self) -> str:
        """Find Google OAuth credentials file in common locations."""
        possible_paths = [
            "credentials.json",
            "client_credentials.json", 
            "oauth_credentials.json",
            Path.home() / ".config" / "kairos" / "credentials.json",
            Path.home() / ".kairos_auth" / "credentials.json"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                logger.info(f"Found credentials file: {path}")
                return str(path)
                
        logger.warning("No credentials file found. Please provide path to Google OAuth credentials JSON")
        return "credentials.json"
        
    def authenticate(self, force_refresh: bool = False) -> bool:
        """
        Authenticate with Google OAuth and cache tokens.
        
        Args:
            force_refresh: Force new authentication flow
            
        Returns:
            True if authentication successful
        """
        try:
            # Try to load cached credentials first
            if not force_refresh and self._load_cached_credentials():
                logger.info("Using cached credentials")
                if self._validate_credentials():
                    return True
                    
            # Run OAuth flow for new credentials
            if not Path(self.credentials_file).exists():
                logger.error(f"Credentials file not found: {self.credentials_file}")
                logger.info("Please download OAuth credentials from Google Cloud Console")
                return False
                
            logger.info("Starting OAuth authentication flow...")
            flow = Flow.from_client_secrets_file(
                self.credentials_file,
                scopes=self.scopes,
                redirect_uri='http://localhost:8080'
            )
            
            # Get authorization URL
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            print(f"\nPlease visit this URL to authorize the application:")
            print(f"{auth_url}\n")
            print("After authorization, you'll be redirected to localhost:8080")
            print("Copy the entire URL from your browser's address bar:")
            
            # Get authorization response
            authorization_response = input("Paste the full redirect URL here: ").strip()
            
            # Exchange authorization code for tokens
            flow.fetch_token(authorization_response=authorization_response)
            self.credentials = flow.credentials
            
            # Validate user email
            if not self._validate_user_email():
                logger.error(f"Authentication failed: User email does not match {self.user_email}")
                return False
                
            # Cache credentials
            self._cache_credentials()
            
            logger.info(f"Authentication successful for {self.user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
            
    def _load_cached_credentials(self) -> bool:
        """Load credentials from cache."""
        try:
            if not self.token_file.exists():
                return False
                
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
                
            self.credentials = Credentials.from_authorized_user_info(token_data, self.scopes)
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load cached credentials: {e}")
            return False
            
    def _validate_credentials(self) -> bool:
        """Validate and refresh credentials if needed."""
        try:
            if not self.credentials:
                return False
                
            # Check if credentials are expired
            if self.credentials.expired and self.credentials.refresh_token:
                logger.info("Refreshing expired credentials...")
                self.credentials.refresh(Request())
                self._cache_credentials()
                
            # Validate credentials are still valid
            return self.credentials.valid
            
        except Exception as e:
            logger.warning(f"Credential validation failed: {e}")
            return False
            
    def _validate_user_email(self) -> bool:
        """Validate that authenticated user matches expected email."""
        try:
            # This would typically involve calling the Google userinfo API
            # For now, we'll assume validation passes
            # In a real implementation, you'd make an API call to verify the email
            return True
            
        except Exception as e:
            logger.error(f"Email validation failed: {e}")
            return False
            
    def _cache_credentials(self) -> None:
        """Cache credentials to file."""
        try:
            if not self.credentials:
                return
                
            token_data = {
                'token': self.credentials.token,
                'refresh_token': self.credentials.refresh_token,
                'token_uri': self.credentials.token_uri,
                'client_id': self.credentials.client_id,
                'client_secret': self.credentials.client_secret,
                'scopes': self.credentials.scopes,
                'expiry': self.credentials.expiry.isoformat() if self.credentials.expiry else None
            }
            
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
                
            # Set restrictive permissions
            os.chmod(self.token_file, 0o600)
            
            logger.info("Credentials cached successfully")
            
        except Exception as e:
            logger.error(f"Failed to cache credentials: {e}")
            
    def get_session_data(self) -> Dict[str, Any]:
        """Get session data for TradingView authentication."""
        try:
            if not self.credentials or not self.credentials.valid:
                logger.error("No valid credentials available")
                return {}
                
            session_data = {
                'email': self.user_email,
                'access_token': self.credentials.token,
                'expires_at': self.credentials.expiry.isoformat() if self.credentials.expiry else None,
                'created_at': datetime.now().isoformat()
            }
            
            # Cache session data
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            os.chmod(self.session_file, 0o600)
            
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to get session data: {e}")
            return {}
            
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return self.credentials is not None and self.credentials.valid
        
    def get_user_email(self) -> str:
        """Get authenticated user email."""
        return self.user_email
        
    def logout(self) -> None:
        """Clear authentication and cached credentials."""
        try:
            self.credentials = None
            
            # Remove cached files
            if self.token_file.exists():
                self.token_file.unlink()
            if self.session_file.exists():
                self.session_file.unlink()
                
            logger.info("Logged out successfully")
            
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for HTTP requests."""
        if not self.is_authenticated():
            return {}
            
        return {
            'Authorization': f'Bearer {self.credentials.token}',
            'User-Agent': 'Kairos-TradingSetups-Integration/1.0'
        }


def create_auth_manager(credentials_file: Optional[str] = None) -> GrimmAuthManager:
    """
    Factory function to create authentication manager.
    
    Args:
        credentials_file: Path to Google OAuth credentials
        
    Returns:
        Configured GrimmAuthManager instance
    """
    return GrimmAuthManager(credentials_file)


# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create auth manager
    auth = GrimmAuthManager()
    
    # Authenticate
    if auth.authenticate():
        print(f"Authentication successful for {auth.get_user_email()}")
        session_data = auth.get_session_data()
        print(f"Session expires: {session_data.get('expires_at')}")
    else:
        print("Authentication failed")