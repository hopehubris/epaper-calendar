#!/usr/bin/env python3
"""Google Calendar OAuth token generation script."""

import sys
import logging
from pathlib import Path
import pickle
import json

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from src import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Calendar API scopes
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def generate_oauth_credentials():
    """Generate OAuth credentials for Google Calendar API.
    
    This script will:
    1. Open your browser to Google's OAuth consent page
    2. Ask you to authorize the app to access your Google Calendar
    3. Save the token to token.json for future use
    """
    
    credentials_path = Path(config.CREDENTIALS_PATH)
    token_path = Path(config.TOKEN_PATH)
    
    # Check if credentials.json exists
    if not credentials_path.exists():
        print(f"Error: {credentials_path} not found")
        print("\nTo set up OAuth:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project")
        print("3. Enable 'Google Calendar API'")
        print("4. Create OAuth 2.0 Desktop Client credentials")
        print("5. Download the credentials JSON file")
        print(f"6. Save it as {credentials_path}")
        sys.exit(1)
    
    try:
        logger.info(f"Using credentials from: {credentials_path}")
        
        # Create OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path),
            SCOPES
        )
        
        # Run local server to handle OAuth callback
        logger.info("Opening browser for OAuth authorization...")
        creds = flow.run_local_server(port=0)
        
        # Save token
        with open(token_path, "wb") as token_file:
            pickle.dump(creds, token_file)
        
        logger.info(f"Token saved to: {token_path}")
        logger.info("OAuth setup complete!")
        
        return True
        
    except FileNotFoundError:
        logger.error(f"Credentials file not found: {credentials_path}")
        return False
    except Exception as e:
        logger.error(f"OAuth setup failed: {e}")
        return False

def refresh_token():
    """Refresh existing OAuth token."""
    token_path = Path(config.TOKEN_PATH)
    
    if not token_path.exists():
        logger.error(f"Token file not found: {token_path}")
        return False
    
    try:
        with open(token_path, "rb") as token_file:
            creds = pickle.load(token_file)
        
        if creds.expired and creds.refresh_token:
            logger.info("Token expired, refreshing...")
            creds.refresh(Request())
            
            # Save refreshed token
            with open(token_path, "wb") as token_file:
                pickle.dump(creds, token_file)
            
            logger.info("Token refreshed successfully")
            return True
        else:
            logger.info("Token is still valid")
            return True
            
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        return False

def verify_credentials():
    """Verify credentials and token are valid."""
    credentials_path = Path(config.CREDENTIALS_PATH)
    token_path = Path(config.TOKEN_PATH)
    
    print("\n" + "=" * 60)
    print("OAuth Credentials Verification")
    print("=" * 60)
    
    # Check credentials file
    if credentials_path.exists():
        print(f"✓ Credentials file: {credentials_path}")
    else:
        print(f"✗ Credentials file: {credentials_path} (missing)")
        return False
    
    # Check token file
    if token_path.exists():
        print(f"✓ Token file: {token_path}")
        
        try:
            with open(token_path, "rb") as f:
                creds = pickle.load(f)
            
            print(f"✓ Token is valid (scopes: {len(creds.scopes)} scope(s))")
            
            if creds.expired:
                print("⚠ Token is expired (will refresh automatically)")
            else:
                print("✓ Token is not expired")
            
            return True
        except Exception as e:
            print(f"✗ Token error: {e}")
            return False
    else:
        print(f"✗ Token file: {token_path} (missing)")
        return False

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Google Calendar OAuth setup"
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate new OAuth credentials"
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh existing token"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify credentials are valid"
    )
    
    args = parser.parse_args()
    
    if args.generate:
        success = generate_oauth_credentials()
        sys.exit(0 if success else 1)
    
    elif args.refresh:
        success = refresh_token()
        sys.exit(0 if success else 1)
    
    elif args.verify:
        success = verify_credentials()
        sys.exit(0 if success else 1)
    
    else:
        # Default: verify then generate if needed
        if verify_credentials():
            print("\n✓ OAuth is configured correctly!")
        else:
            print("\n→ Running OAuth setup...")
            success = generate_oauth_credentials()
            
            if success:
                print("\n✓ OAuth setup complete!")
                verify_credentials()
            else:
                print("\n✗ OAuth setup failed")
                sys.exit(1)

if __name__ == "__main__":
    main()
