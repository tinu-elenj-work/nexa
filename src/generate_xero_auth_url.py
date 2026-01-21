"""
Generate Xero OAuth2 Authorization URL

This script generates the authorization URL for Xero OAuth2.
You'll need to visit this URL in your browser to authorize the app.

Usage:
    python src/generate_xero_auth_url.py
"""

import os
import sys
import urllib.parse
import webbrowser

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import XERO_CONFIG

def generate_authorization_url():
    """Generate the Xero OAuth2 authorization URL"""
    
    # Xero OAuth2 endpoints
    auth_url = "https://login.xero.com/identity/connect/authorize"
    
    # Required parameters
    params = {
        'response_type': 'code',
        'client_id': XERO_CONFIG['client_id'],
        'redirect_uri': 'http://localhost:8080/callback',
        'scope': ' '.join(XERO_CONFIG['scopes']),
        'state': 'xero_oauth_setup'
    }
    
    # Build the full URL
    query_string = urllib.parse.urlencode(params)
    full_url = f"{auth_url}?{query_string}"
    
    return full_url

def main():
    """Main function"""
    
    print("🔗 Xero OAuth2 Authorization URL Generator")
    print("=" * 60)
    print()
    
    auth_url = generate_authorization_url()
    
    print("📋 Follow these steps to authorize the app:")
    print()
    print("1. Click the URL below (or copy and paste it into your browser)")
    print("2. Log in to Xero and authorize the app")
    print("3. You'll be redirected to a URL like:")
    print("   http://localhost:8080/callback?code=ABC123&state=xero_oauth_setup")
    print("4. Copy the 'code' value from the URL (e.g., 'ABC123')")
    print("5. Run: python src/exchange_code_for_tokens.py <code>")
    print()
    print("-" * 60)
    print("Authorization URL:")
    print("-" * 60)
    print(auth_url)
    print("-" * 60)
    print()
    
    # Try to open browser
    try:
        response = input("Open this URL in your browser now? (Y/n): ").strip().lower()
        if response != 'n':
            webbrowser.open(auth_url)
            print("✅ Browser opened!")
    except:
        # If input fails (non-interactive), just open the browser
        try:
            webbrowser.open(auth_url)
            print("✅ Browser opened!")
        except:
            pass
    
    print()
    print("After authorization, run:")
    print("  python src/exchange_code_for_tokens.py <authorization_code>")

if __name__ == "__main__":
    main()
