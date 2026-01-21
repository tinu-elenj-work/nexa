import requests
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os
from pathlib import Path

class ElapseITAPIClient:
    """Client for interacting with ElapseIT API"""
    
    def __init__(self, domain: str, username: str, password: str, timezone: str = "Europe/London", api_base_url: str = None):
        """
        Initialize the ElapseIT API client
        
        Args:
            domain: Your ElapseIT domain for authentication (e.g., "elenjicalsolutions.com")
            username: Your ElapseIT username
            password: Your ElapseIT password
            timezone: Your timezone (default: Europe/London)
            api_base_url: Optional custom API base URL (defaults to app.elapseit.com)
        """
        self.domain = domain
        self.username = username
        self.password = password
        self.timezone = timezone
        
        # API endpoints
        self.auth_url = "https://auth.elapseit.net/oauth2/token"
        
        # Use custom API base URL or default to app.elapseit.com
        if api_base_url:
            self.base_url = api_base_url
        else:
            self.base_url = "https://app.elapseit.com"
        
        # Token management
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
        # Session for making requests
        self.session = requests.Session()
        self.session.headers.update({
            'Origin': f'https://{domain}',
            'User-Agent': 'ElapseIT-API-Client/1.0'
        })
    
    def authenticate(self) -> bool:
        """
        Authenticate with ElapseIT and retrieve access token
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Prepare authentication data
            auth_data = {
                'username': self.username,
                'password': self.password,
                'rememberMe': 'true',
                'grant_type': 'password',
                'timezone': self.timezone
            }
            
            print(f"🔐 Authenticating with ElapseIT domain: {self.domain}")
            
            # Make authentication request
            response = self.session.post(
                self.auth_url,
                data=auth_data,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Store token information
                self.access_token = token_data.get('access_token')
                self.refresh_token = token_data.get('refresh_token')
                expires_in = token_data.get('expires_in', 899)  # Default 899 seconds
                
                # Calculate expiration time
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                # Update session headers with authorization
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                print(f"✅ Authentication successful!")
                print(f"   Token expires at: {self.token_expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Token type: {token_data.get('token_type', 'Unknown')}")
                
                return True
            else:
                print(f"❌ Authentication failed!")
                print(f"   Status code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Authentication request failed: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse authentication response: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during authentication: {e}")
            return False
    
    def refresh_token_if_needed(self) -> bool:
        """
        Refresh the access token if it's expired or about to expire
        
        Returns:
            bool: True if token is valid or refreshed successfully, False otherwise
        """
        # Check if token is expired or will expire in the next 5 minutes
        if (self.token_expires_at is None or 
            datetime.now() + timedelta(minutes=5) >= self.token_expires_at):
            
            if self.refresh_token:
                print("🔄 Access token expired, refreshing...")
                return self._refresh_access_token()
            else:
                print("❌ No refresh token available, need to re-authenticate")
                return self.authenticate()
        
        return True
    
    def _refresh_access_token(self) -> bool:
        """
        Refresh the access token using the refresh token
        
        Returns:
            bool: True if refresh successful, False otherwise
        """
        try:
            # Prepare refresh data
            refresh_data = {
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token'
            }
            
            # Make refresh request
            response = self.session.post(
                self.auth_url,
                data=refresh_data,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Update token information
                self.access_token = token_data.get('access_token')
                self.refresh_token = token_data.get('refresh_token', self.refresh_token)
                expires_in = token_data.get('expires_in', 899)
                
                # Calculate new expiration time
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                # Update session headers
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                print(f"✅ Token refreshed successfully!")
                print(f"   New token expires at: {self.token_expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
                
                return True
            else:
                print(f"❌ Token refresh failed!")
                print(f"   Status code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Token refresh request failed: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse refresh response: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during token refresh: {e}")
            return False
    
    def make_api_request(self, endpoint: str, method: str = 'GET', params: Optional[Dict] = None, 
                        data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make an authenticated API request
        
        Args:
            endpoint: API endpoint (e.g., '/projects', '/allocations')
            method: HTTP method (GET, POST, PUT, DELETE)
            params: Query parameters
            data: Request body data
            
        Returns:
            Dict: API response data or None if request failed
        """
        # Ensure we have a valid token
        if not self.refresh_token_if_needed():
            print("❌ Failed to obtain valid access token")
            return None
        
        try:
            url = f"{self.base_url}{endpoint}"
            
            print(f"🌐 Making {method} request to: {endpoint}")
            
            # Make the request
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=30)
            else:
                print(f"❌ Unsupported HTTP method: {method}")
                return None
            
            # Handle response
            if response.status_code == 200:
                print(f"✅ Request successful")
                return response.json()
            elif response.status_code == 401:
                print(f"❌ Unauthorized - Token may be invalid or insufficient permissions")
                return None
            elif response.status_code == 403:
                print(f"❌ Forbidden - Insufficient permissions for this endpoint")
                return None
            elif response.status_code == 404:
                print(f"❌ Not Found - Endpoint does not exist")
                return None
            else:
                print(f"❌ Request failed with status code: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse API response: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error during API request: {e}")
            return None
    
    def get_projects(self, params: Optional[Dict] = None) -> Optional[List[Dict]]:
        """
        Retrieve projects from ElapseIT
        
        Args:
            params: Optional query parameters
            
        Returns:
            List of projects or None if request failed
        """
        response = self.make_api_request('/public/v1/Projects', params=params)
        if response and 'value' in response:
            return response['value']
        return response
    
    def get_allocations(self, params: Optional[Dict] = None) -> Optional[List[Dict]]:
        """
        Retrieve allocations from ElapseIT
        
        Args:
            params: Optional query parameters
            
        Returns:
            List of allocations or None if request failed
        """
        response = self.make_api_request('/public/v1/ProjectPersonAllocations', params=params)
        if response and 'value' in response:
            return response['value']
        return response
    
    def get_clients(self, params: Optional[Dict] = None) -> Optional[List[Dict]]:
        """
        Retrieve clients from ElapseIT
        
        Args:
            params: Optional query parameters
            
        Returns:
            List of clients or None if request failed
        """
        response = self.make_api_request('/public/v1/Clients', params=params)
        if response and 'value' in response:
            return response['value']
        return response
    
    def get_people(self, params: Optional[Dict] = None) -> Optional[List[Dict]]:
        """
        Retrieve people/employees from ElapseIT
        
        Args:
            params: Optional query parameters
            
        Returns:
            List of people or None if request failed
        """
        response = self.make_api_request('/public/v1/People', params=params)
        if response and 'value' in response:
            return response['value']
        return response
    
    def export_data_to_csv(self, data: List[Dict], filename: str, output_dir: str = "api_exports"):
        """
        Export API data to CSV format
        
        Args:
            data: List of dictionaries to export
            filename: Name of the CSV file
            output_dir: Output directory for CSV files
        """
        if not data:
            print(f"❌ No data to export for {filename}")
            return
        
        try:
            # Create output directory if it doesn't exist
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Create full file path
            file_path = output_path / f"{filename}.csv"
            
            # Convert to CSV
            import csv
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                if data:
                    # Get fieldnames from first item
                    fieldnames = list(data[0].keys())
                    
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
            
            print(f"✅ Data exported to: {file_path}")
            print(f"   Records exported: {len(data)}")
            
        except Exception as e:
            print(f"❌ Failed to export data to CSV: {e}")
    
    def close(self):
        """Close the API client session"""
        if self.session:
            self.session.close()
        print("🔒 API client session closed")


def main():
    """Example usage of the ElapseIT API client"""
    
    # Configuration - Replace with your actual values
    config = {
        'domain': 'yourdomain',  # Replace with your ElapseIT domain
        'username': 'your_username',  # Replace with your username
        'password': 'your_password',  # Replace with your password
        'timezone': 'Europe/London'  # Replace with your timezone
    }
    
    # Create API client
    client = ElapseITAPIClient(**config)
    
    try:
        # Authenticate
        if not client.authenticate():
            print("❌ Failed to authenticate. Exiting.")
            return
        
        print("\n" + "="*60)
        print("RETRIEVING ELAPSEIT DATA VIA API")
        print("="*60)
        
        # Example: Retrieve projects
        print("\n📋 Retrieving projects...")
        projects = client.get_projects()
        if projects:
            print(f"   Found {len(projects)} projects")
            # Export to CSV
            client.export_data_to_csv(projects, 'projects_api')
        
        # Example: Retrieve allocations
        print("\n📊 Retrieving allocations...")
        allocations = client.get_allocations()
        if allocations:
            print(f"   Found {len(allocations)} allocations")
            # Export to CSV
            client.export_data_to_csv(allocations, 'allocations_api')
        
        # Example: Retrieve clients
        print("\n🏢 Retrieving clients...")
        clients = client.get_clients()
        if clients:
            print(f"   Found {len(clients)} clients")
            # Export to CSV
            client.export_data_to_csv(clients, 'clients_api')
        
        # Example: Retrieve people
        print("\n👥 Retrieving people...")
        people = client.get_people()
        if people:
            print(f"   Found {len(people)} people")
            # Export to CSV
            client.export_data_to_csv(people, 'people_api')
        
        print("\n✅ Data retrieval complete!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Operation interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        # Always close the client
        client.close()


if __name__ == "__main__":
    main()
