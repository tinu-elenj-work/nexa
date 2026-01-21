"""
Unit tests for ElapseIT API Client
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from elapseit_api_client import ElapseITAPIClient


class TestElapseITAPIClient:
    """Test cases for ElapseIT API Client"""
    
    def test_init(self):
        """Test client initialization"""
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password',
            timezone='Europe/London'
        )
        
        assert client.domain == 'test.com'
        assert client.username == 'test@test.com'
        assert client.password == 'password'
        assert client.timezone == 'Europe/London'
        assert client.auth_url == 'https://auth.elapseit.net/oauth2/token'
        assert client.api_base_url == 'https://app.elapseit.com'
    
    def test_init_with_custom_api_url(self):
        """Test client initialization with custom API URL"""
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password',
            timezone='Europe/London',
            api_base_url='https://custom.elapseit.com'
        )
        
        assert client.api_base_url == 'https://custom.elapseit.com'
    
    @patch('requests.post')
    def test_authenticate_success(self, mock_post):
        """Test successful authentication"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_token',
            'token_type': 'Bearer',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response
        
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password'
        )
        
        result = client.authenticate()
        
        assert result is True
        assert client.access_token == 'test_token'
        assert client.token_type == 'Bearer'
        assert client.token_expires_at is not None
        
        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['url'] == 'https://auth.elapseit.net/oauth2/token'
        assert 'username' in call_args[1]['data']
        assert 'password' in call_args[1]['data']
        assert 'domain' in call_args[1]['data']
    
    @patch('requests.post')
    def test_authenticate_failure(self, mock_post):
        """Test authentication failure"""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'error': 'invalid_credentials'}
        mock_post.return_value = mock_response
        
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='wrong_password'
        )
        
        result = client.authenticate()
        
        assert result is False
        assert client.access_token is None
    
    @patch('requests.post')
    def test_authenticate_exception(self, mock_post):
        """Test authentication with exception"""
        mock_post.side_effect = Exception("Network error")
        
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password'
        )
        
        result = client.authenticate()
        
        assert result is False
        assert client.access_token is None
    
    def test_is_token_valid_no_token(self):
        """Test token validation with no token"""
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password'
        )
        
        assert client.is_token_valid() is False
    
    def test_is_token_valid_expired_token(self):
        """Test token validation with expired token"""
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password'
        )
        client.access_token = 'test_token'
        client.token_expires_at = datetime.now().timestamp() - 100  # Expired
        
        assert client.is_token_valid() is False
    
    def test_is_token_valid_valid_token(self):
        """Test token validation with valid token"""
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password'
        )
        client.access_token = 'test_token'
        client.token_expires_at = datetime.now().timestamp() + 3600  # Valid for 1 hour
        
        assert client.is_token_valid() is True
    
    @patch('requests.get')
    def test_get_clients_success(self, mock_get):
        """Test successful clients retrieval"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'ID': 1,
                'Code': 'CLI001',
                'Name': 'Test Client',
                'IsArchived': False
            }
        ]
        mock_get.return_value = mock_response
        
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password'
        )
        client.access_token = 'test_token'
        client.token_type = 'Bearer'
        
        result = client.get_clients()
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['ID'] == 1
        assert result[0]['Name'] == 'Test Client'
        
        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'Authorization' in call_args[1]['headers']
        assert call_args[1]['headers']['Authorization'] == 'Bearer test_token'
    
    @patch('requests.get')
    def test_get_clients_unauthorized(self, mock_get):
        """Test clients retrieval with unauthorized response"""
        # Mock unauthorized response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password'
        )
        client.access_token = 'test_token'
        
        result = client.get_clients()
        
        assert result is None
    
    @patch('requests.get')
    def test_get_people_success(self, mock_get):
        """Test successful people retrieval"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'ID': 1,
                'FirstName': 'John',
                'LastName': 'Doe',
                'Email': 'john.doe@test.com',
                'IsActive': True
            }
        ]
        mock_get.return_value = mock_response
        
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password'
        )
        client.access_token = 'test_token'
        client.token_type = 'Bearer'
        
        result = client.get_people()
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['ID'] == 1
        assert result[0]['FirstName'] == 'John'
    
    @patch('requests.get')
    def test_get_projects_success(self, mock_get):
        """Test successful projects retrieval"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'ID': 1,
                'Code': 'PROJ001',
                'Name': 'Test Project',
                'ClientID': 1,
                'Status': 'Active'
            }
        ]
        mock_get.return_value = mock_response
        
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password'
        )
        client.access_token = 'test_token'
        client.token_type = 'Bearer'
        
        result = client.get_projects()
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['ID'] == 1
        assert result[0]['Name'] == 'Test Project'
    
    @patch('requests.get')
    def test_get_allocations_success(self, mock_get):
        """Test successful allocations retrieval"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'ID': 1,
                'ProjectID': 1,
                'PersonID': 1,
                'StartDate': '2023-01-01T00:00:00Z',
                'EndDate': '2023-12-31T00:00:00Z',
                'AllocationPercent': 100
            }
        ]
        mock_get.return_value = mock_response
        
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password'
        )
        client.access_token = 'test_token'
        client.token_type = 'Bearer'
        
        result = client.get_allocations()
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['ID'] == 1
        assert result[0]['AllocationPercent'] == 100
    
    @patch('requests.get')
    def test_get_timesheet_records_success(self, mock_get):
        """Test successful timesheet records retrieval"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'ID': 1,
                'PersonID': 1,
                'ProjectID': 1,
                'Date': '2023-01-01',
                'Hours': 8.0,
                'Description': 'Development work'
            }
        ]
        mock_get.return_value = mock_response
        
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password'
        )
        client.access_token = 'test_token'
        client.token_type = 'Bearer'
        
        result = client.get_timesheet_records('2023-01-01', '2023-01-31')
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['ID'] == 1
        assert result[0]['Hours'] == 8.0
    
    def test_get_all_data_no_authentication(self):
        """Test get_all_data without authentication"""
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password'
        )
        
        result = client.get_all_data()
        
        assert result is None
    
    @patch.object(ElapseITAPIClient, 'authenticate')
    @patch.object(ElapseITAPIClient, 'get_clients')
    @patch.object(ElapseITAPIClient, 'get_people')
    @patch.object(ElapseITAPIClient, 'get_projects')
    @patch.object(ElapseITAPIClient, 'get_allocations')
    def test_get_all_data_success(self, mock_allocations, mock_projects, 
                                 mock_people, mock_clients, mock_auth):
        """Test successful get_all_data"""
        # Mock authentication
        mock_auth.return_value = True
        
        # Mock data retrieval
        mock_clients.return_value = [{'ID': 1, 'Name': 'Test Client'}]
        mock_people.return_value = [{'ID': 1, 'FirstName': 'John'}]
        mock_projects.return_value = [{'ID': 1, 'Name': 'Test Project'}]
        mock_allocations.return_value = [{'ID': 1, 'ProjectID': 1}]
        
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password'
        )
        
        result = client.get_all_data()
        
        assert result is not None
        assert 'clients' in result
        assert 'people' in result
        assert 'projects' in result
        assert 'allocations' in result
        assert len(result['clients']) == 1
        assert len(result['people']) == 1
        assert len(result['projects']) == 1
        assert len(result['allocations']) == 1
    
    @patch.object(ElapseITAPIClient, 'authenticate')
    def test_get_all_data_auth_failure(self, mock_auth):
        """Test get_all_data with authentication failure"""
        mock_auth.return_value = False
        
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password'
        )
        
        result = client.get_all_data()
        
        assert result is None
    
    def test_export_to_csv(self, temp_dir):
        """Test CSV export functionality"""
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password'
        )
        
        test_data = {
            'clients': [{'ID': 1, 'Name': 'Test Client'}],
            'people': [{'ID': 1, 'FirstName': 'John'}],
            'projects': [{'ID': 1, 'Name': 'Test Project'}],
            'allocations': [{'ID': 1, 'ProjectID': 1}]
        }
        
        output_dir = os.path.join(temp_dir, 'exports')
        result = client.export_to_csv(test_data, output_dir)
        
        assert result is True
        assert os.path.exists(output_dir)
        assert os.path.exists(os.path.join(output_dir, 'clients.csv'))
        assert os.path.exists(os.path.join(output_dir, 'people.csv'))
        assert os.path.exists(os.path.join(output_dir, 'projects.csv'))
        assert os.path.exists(os.path.join(output_dir, 'allocations.csv'))
    
    def test_export_to_csv_empty_data(self, temp_dir):
        """Test CSV export with empty data"""
        client = ElapseITAPIClient(
            domain='test.com',
            username='test@test.com',
            password='password'
        )
        
        test_data = {
            'clients': [],
            'people': [],
            'projects': [],
            'allocations': []
        }
        
        output_dir = os.path.join(temp_dir, 'exports')
        result = client.export_to_csv(test_data, output_dir)
        
        assert result is True
        assert os.path.exists(output_dir)
