"""
Xero Token Refresh Script

This script refreshes the Xero OAuth2 access token using the refresh token.
No user interaction required.

Usage:
    python src/refresh_xero_token.py
"""

import os
import sys
import base64
import requests
import re

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import XERO_CONFIG

def refresh_xero_token():
    """Refresh Xero OAuth2 access token using refresh token"""
    
    print("🔄 Refreshing Xero OAuth2 Token")
    print("=" * 50)
    print()
    
    # Check if we have a refresh token
    if not XERO_CONFIG.get('refresh_token') or XERO_CONFIG['refresh_token'] == 'YOUR_REFRESH_TOKEN':
        print("❌ No refresh token found in config")
        print("Please run the OAuth setup script first: python src/xero_oauth_setup.py")
        return False
    
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
        'grant_type': 'refresh_token',
        'refresh_token': XERO_CONFIG['refresh_token']
    }
    
    try:
        print("📡 Requesting new tokens from Xero...")
        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            
            print("✅ Tokens received successfully!")
            print(f"   Access Token: {token_data['access_token'][:30]}...")
            if 'refresh_token' in token_data:
                print(f"   Refresh Token: {token_data['refresh_token'][:30]}...")
            print(f"   Expires In: {token_data.get('expires_in', 'unknown')} seconds")
            print()
            
            # Update config file
            print("💾 Updating config file...")
            config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.py')
            
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                
                # Update access_token
                config_content = re.sub(
                    r"'access_token': '[^']*'",
                    f"'access_token': '{token_data['access_token']}'",
                    config_content
                )
                
                # Update refresh_token if provided
                if 'refresh_token' in token_data:
                    config_content = re.sub(
                        r"'refresh_token': '[^']*'",
                        f"'refresh_token': '{token_data['refresh_token']}'",
                        config_content
                    )
                
                # Write back to file
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(config_content)
                
                print("✅ Config file updated successfully!")
                print()
                print("🎉 Token refresh completed!")
                print("You can now use the Xero API with the new tokens.")
                return True
                
            except Exception as e:
                print(f"❌ Error updating config file: {e}")
                print()
                print("⚠️  Tokens received but could not save to config file.")
                print("Please manually update config/config.py with:")
                print(f"   access_token: {token_data['access_token']}")
                if 'refresh_token' in token_data:
                    print(f"   refresh_token: {token_data['refresh_token']}")
                return False
                
        else:
            print(f"❌ Failed to refresh token")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            print()
            
            if response.status_code == 401:
                print("⚠️  Refresh token may have expired.")
                print("You need to re-authenticate using:")
                print("   python src/xero_oauth_server.py")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error refreshing token: {e}")
        return False

if __name__ == "__main__":
    success = refresh_xero_token()
    sys.exit(0 if success else 1)
