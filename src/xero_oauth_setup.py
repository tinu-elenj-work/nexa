"""
Xero OAuth2 Setup Script

This script helps you set up OAuth2 authentication for Xero API.
It will generate the authorization URL and help you get the initial tokens.

Usage:
    python src/xero_oauth_setup.py
"""

import os
import sys
import webbrowser
import base64
import urllib.parse
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import XERO_CONFIG

def generate_authorization_url():
    """Generate the Xero OAuth2 authorization URL"""
    
    # Xero OAuth2 endpoints
    auth_url = "https://login.xero.com/identity/connect/authorize"
    
    # Required parameters - using your configured redirect URI
    params = {
        'response_type': 'code',
        'client_id': XERO_CONFIG['client_id'],
        'redirect_uri': 'http://localhost:8080/callback',  # Your configured redirect URI
        'scope': ' '.join(XERO_CONFIG['scopes']),
        'state': 'xero_oauth_setup'
    }
    
    # Build the full URL
    query_string = urllib.parse.urlencode(params)
    full_url = f"{auth_url}?{query_string}"
    
    return full_url

def get_tokens_from_code(authorization_code):
    """Exchange authorization code for access and refresh tokens"""
    
    token_url = "https://identity.xero.com/connect/token"
    
    # Create basic auth header
    credentials = base64.b64encode(
        f"{XERO_CONFIG['client_id']}:{XERO_CONFIG['client_secret']}".encode()
    ).decode()
    
    headers = {
        'Authorization': f'Basic {credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': 'http://localhost:8080/callback'
    }
    
    import requests
    
    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        return token_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting tokens: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

def update_config_file(access_token, refresh_token, expires_in=1800):
    """Update the config.py file with new tokens"""
    
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.py')
    
    try:
        # Read current config
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Update access token
        import re
        content = re.sub(
            r"'access_token': '[^']*'",
            f"'access_token': '{access_token}'",
            content
        )
        
        # Update refresh token
        content = re.sub(
            r"'refresh_token': '[^']*'",
            f"'refresh_token': '{refresh_token}'",
            content
        )
        
        # Write back to file
        with open(config_file, 'w') as f:
            f.write(content)
        
        print("✅ Config file updated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating config file: {e}")
        return False

def main():
    """Main OAuth2 setup process"""
    
    print("🚀 Xero OAuth2 Setup")
    print("=" * 50)
    print()
    
    # Check if we already have valid tokens
    if (XERO_CONFIG['access_token'] != 'test_access_token' and 
        XERO_CONFIG['refresh_token'] != 'test_refresh_token'):
        print("✅ You already have tokens configured!")
        print(f"Access Token: {XERO_CONFIG['access_token'][:20]}...")
        print(f"Refresh Token: {XERO_CONFIG['refresh_token'][:20]}...")
        print()
        
        response = input("Do you want to set up new tokens? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    print("📋 OAuth2 Setup Process:")
    print("1. Generate authorization URL")
    print("2. Open browser for user authorization")
    print("3. Get authorization code from redirect")
    print("4. Exchange code for tokens")
    print("5. Update config file")
    print()
    
    # Step 1: Generate authorization URL
    print("🔗 Generating authorization URL...")
    auth_url = generate_authorization_url()
    print(f"Authorization URL: {auth_url}")
    print()
    
    # Step 2: Open browser
    print("🌐 Opening browser for authorization...")
    print("Please authorize the app and copy the authorization code from the redirect URL.")
    print()
    
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened. Please complete the authorization process.")
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print("Please manually open the URL above in your browser.")
    
    print()
    print("📝 After authorization, you'll be redirected to a URL like:")
    print("http://localhost:8080/callback?code=ABC123&state=xero_oauth_setup")
    print()
    print("Copy the 'code' parameter value (e.g., 'ABC123')")
    print()
    print("⚠️  Note: Make sure you have a local server running on port 8080")
    print("Or you can manually copy the code from the browser URL")
    print()
    
    # Step 3: Get authorization code
    auth_code = input("Enter the authorization code: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided. Setup cancelled.")
        return
    
    # Step 4: Exchange code for tokens
    print("🔄 Exchanging authorization code for tokens...")
    token_data = get_tokens_from_code(auth_code)
    
    if not token_data:
        print("❌ Failed to get tokens. Setup cancelled.")
        return
    
    print("✅ Tokens received successfully!")
    print(f"Access Token: {token_data['access_token'][:20]}...")
    print(f"Refresh Token: {token_data['refresh_token'][:20]}...")
    print(f"Expires In: {token_data.get('expires_in', 'unknown')} seconds")
    print()
    
    # Step 5: Update config file
    print("💾 Updating config file...")
    success = update_config_file(
        token_data['access_token'],
        token_data['refresh_token'],
        token_data.get('expires_in', 1800)
    )
    
    if success:
        print()
        print("🎉 OAuth2 setup completed successfully!")
        print("You can now use the Xero API with the new tokens.")
        print()
        print("Next steps:")
        print("1. Test the connection: python src/get_xero_reports.py 'June 2025'")
        print("2. The tokens will be automatically refreshed when needed")
    else:
        print("❌ Setup completed but config file update failed.")
        print("Please manually update the tokens in config/config.py")

if __name__ == "__main__":
    main()
