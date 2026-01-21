"""
Exchange Xero Authorization Code for Tokens

This script exchanges an authorization code for access and refresh tokens.

Usage:
    python src/exchange_code_for_tokens.py <authorization_code>
"""

import os
import sys
import base64
import requests
import re

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import XERO_CONFIG

def exchange_code_for_tokens(authorization_code):
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
    
    try:
        print("🔄 Exchanging authorization code for tokens...")
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
                print("🎉 OAuth2 setup completed!")
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
            print(f"❌ Failed to exchange code for tokens")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error exchanging code: {e}")
        return False

def main():
    """Main function"""
    
    if len(sys.argv) < 2:
        print("❌ Missing authorization code")
        print()
        print("Usage:")
        print("  python src/exchange_code_for_tokens.py <authorization_code>")
        print()
        print("To get an authorization code:")
        print("  1. Run: python src/generate_xero_auth_url.py")
        print("  2. Authorize the app in your browser")
        print("  3. Copy the 'code' from the redirect URL")
        print("  4. Run this script with that code")
        sys.exit(1)
    
    authorization_code = sys.argv[1]
    
    print("🔐 Xero OAuth2 Token Exchange")
    print("=" * 50)
    print()
    
    success = exchange_code_for_tokens(authorization_code)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
