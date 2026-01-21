"""
Xero OAuth2 Server Setup

This script creates a local server to automatically capture the authorization code
from the OAuth2 redirect, eliminating the need for manual copy-paste.

Usage:
    python src/xero_oauth_server.py
"""

import os
import sys
import webbrowser
import urllib.parse
import base64
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import XERO_CONFIG

class OAuthHandler(BaseHTTPRequestHandler):
    """HTTP handler to capture OAuth2 authorization code"""
    
    def do_GET(self):
        """Handle GET requests from OAuth2 redirect"""
        if self.path.startswith('/callback'):
            # Parse query parameters
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            # Check if we have an authorization code
            if 'code' in query_params:
                code = query_params['code'][0]
                print(f"\n✅ Authorization code received: {code}")
                
                # Exchange code for tokens
                print("🔄 Exchanging code for tokens...")
                token_data = self.exchange_code_for_tokens(code)
                
                if token_data:
                    print("✅ Tokens received successfully!")
                    print(f"Access Token: {token_data['access_token'][:20]}...")
                    print(f"Refresh Token: {token_data['refresh_token'][:20]}...")
                    print(f"Expires In: {token_data.get('expires_in', 'unknown')} seconds")
                    
                    # Update config file
                    print("💾 Updating config file...")
                    success = self.update_config_file(
                        token_data['access_token'],
                        token_data['refresh_token'],
                        token_data.get('expires_in', 1800)
                    )
                    
                    if success:
                        print("🎉 OAuth2 setup completed successfully!")
                        print("You can now use the Xero API with the new tokens.")
                    else:
                        print("❌ Config file update failed")
                else:
                    print("❌ Failed to get tokens")
                
                # Send response to browser
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                <html>
                <body>
                    <h1>OAuth2 Setup Complete!</h1>
                    <p>Authorization successful! You can close this window.</p>
                    <p>Check your terminal for the next steps.</p>
                </body>
                </html>
                ''')
                
                # Stop the server
                self.server.shutdown()
            else:
                # No code in URL
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                <html>
                <body>
                    <h1>Error</h1>
                    <p>No authorization code found in URL.</p>
                </body>
                </html>
                ''')
        else:
            # Other paths
            self.send_response(404)
            self.end_headers()
    
    def exchange_code_for_tokens(self, authorization_code):
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
            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting tokens: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def update_config_file(self, access_token, refresh_token, expires_in=1800):
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
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating config file: {e}")
            return False

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
    """Main OAuth2 server setup process"""
    
    print("🚀 Xero OAuth2 Server Setup")
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
    
    print("📋 OAuth2 Server Setup Process:")
    print("1. Start local server on port 8080")
    print("2. Generate authorization URL")
    print("3. Open browser for user authorization")
    print("4. Automatically capture authorization code")
    print("5. Exchange code for tokens")
    print("6. Update config file")
    print()
    
    # Step 1: Start local server
    print("🌐 Starting local server on port 8080...")
    
    try:
        server = HTTPServer(('localhost', 8080), OAuthHandler)
        print("✅ Server started successfully!")
        print("   Listening on: http://localhost:8080")
        print()
        
        # Step 2: Generate authorization URL
        print("🔗 Generating authorization URL...")
        auth_url = generate_authorization_url()
        print(f"Authorization URL: {auth_url}")
        print()
        
        # Step 3: Open browser
        print("🌐 Opening browser for authorization...")
        print("Please authorize the app in the browser window that opens.")
        print("The server will automatically capture the authorization code.")
        print()
        
        try:
            webbrowser.open(auth_url)
            print("✅ Browser opened. Please complete the authorization process.")
        except Exception as e:
            print(f"⚠️ Could not open browser automatically: {e}")
            print("Please manually open the URL above in your browser.")
        
        print()
        print("⏳ Waiting for authorization...")
        print("(The server will automatically stop after receiving the code)")
        print()
        
        # Start server in a separate thread
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait for server to be shut down
        while server_thread.is_alive():
            time.sleep(0.1)
        
        print("✅ OAuth2 setup completed!")
        
    except OSError as e:
        if e.errno == 10048:  # Port already in use
            print("❌ Port 8080 is already in use.")
            print("Please close any applications using port 8080 and try again.")
        else:
            print(f"❌ Error starting server: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
