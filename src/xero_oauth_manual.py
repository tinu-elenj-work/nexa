"""
Xero OAuth2 Manual Setup

This script provides a manual process to get Xero OAuth2 tokens.
It shows you exactly what to do step by step.

Usage:
    python src/xero_oauth_manual.py
"""

import os
import sys
import base64
import urllib.parse
import requests

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import XERO_CONFIG

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
    """Manual OAuth2 setup process"""
    
    print("🚀 Xero OAuth2 Manual Setup")
    print("=" * 50)
    print()
    
    print("📋 Manual Setup Process:")
    print("1. Go to Xero Developer Portal")
    print("2. Find your app and get the authorization URL")
    print("3. Authorize the app and get the code")
    print("4. Enter the tokens here")
    print()
    
    print("🔗 Step 1: Go to Xero Developer Portal")
    print("Visit: https://developer.xero.com/myapps/")
    print("Find your app with Client ID:", XERO_CONFIG['client_id'])
    print()
    
    print("🔗 Step 2: Get Authorization URL")
    print("In your Xero app settings, look for 'Redirect URIs'")
    print("Use one of the configured redirect URIs")
    print()
    
    print("🔗 Step 3: Manual Authorization")
    print("You can also use this URL (replace REDIRECT_URI with your actual redirect URI):")
    
    # Generate authorization URL with placeholder
    auth_url = "https://login.xero.com/identity/connect/authorize"
    params = {
        'response_type': 'code',
        'client_id': XERO_CONFIG['client_id'],
        'redirect_uri': 'YOUR_REDIRECT_URI_HERE',
        'scope': ' '.join(XERO_CONFIG['scopes']),
        'state': 'xero_oauth_setup'
    }
    
    query_string = urllib.parse.urlencode(params)
    full_url = f"{auth_url}?{query_string}"
    print(f"URL: {full_url}")
    print()
    
    print("🔗 Step 4: Alternative - Use Postman/curl")
    print("If you have Postman or curl, you can use this request:")
    print()
    
    # Show the token exchange request
    token_url = "https://identity.xero.com/connect/token"
    credentials = base64.b64encode(
        f"{XERO_CONFIG['client_id']}:{XERO_CONFIG['client_secret']}".encode()
    ).decode()
    
    print("POST", token_url)
    print("Headers:")
    print(f"  Authorization: Basic {credentials}")
    print("  Content-Type: application/x-www-form-urlencoded")
    print("Body:")
    print("  grant_type=authorization_code")
    print("  code=YOUR_AUTHORIZATION_CODE_HERE")
    print("  redirect_uri=YOUR_REDIRECT_URI_HERE")
    print()
    
    print("🔗 Step 5: Enter Tokens Manually")
    print("If you have the tokens from another source, enter them here:")
    print()
    
    # Get tokens manually
    access_token = input("Enter Access Token (or press Enter to skip): ").strip()
    
    if not access_token:
        print("❌ No access token provided. Setup cancelled.")
        return
    
    refresh_token = input("Enter Refresh Token (or press Enter to skip): ").strip()
    
    if not refresh_token:
        print("⚠️  No refresh token provided. You'll need to re-authenticate when the access token expires.")
        refresh_token = "no_refresh_token"
    
    expires_in = input("Enter Expires In (seconds, default 1800): ").strip()
    if not expires_in:
        expires_in = 1800
    else:
        try:
            expires_in = int(expires_in)
        except ValueError:
            expires_in = 1800
    
    print()
    print("💾 Updating config file...")
    success = update_config_file(access_token, refresh_token, expires_in)
    
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
