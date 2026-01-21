"""
Unit tests for Vision Database Client
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from vision_db_client import VisionDBClient


class TestVisionDBClient:
    """Test cases for Vision Database Client"""
    
    def test_init(self):
        """Test client initialization"""
        client = VisionDBClient(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_password'
        )
        
        assert client.connection_params['host'] == 'localhost'
        assert client.connection_params['port'] == 5432
        assert client.connection_params['database'] == 'test_db'
        assert client.connection_params['user'] == 'test_user'
        assert client.connection_params['password'] == 'test_password'
        assert client._connection is None
    
    @patch('psycopg2.connect')
    def test_get_connection_success(self, mock_connect):
        """Test successful database connection"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        client = VisionDBClient(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_password'
        )
        
        with client.get_connection() as conn:
            assert conn == mock_conn
        
        mock_connect.assert_called_once_with(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_password'
        )
    
    @patch('psycopg2.connect')
    def test_get_connection_failure(self, mock_connect):
        """Test database connection failure"""
        mock_connect.side_effect = Exception("Connection failed")
        
        client = VisionDBClient(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_password'
        )
        
        with pytest.raises(Exception):
            with client.get_connection() as conn:
                pass
    
    @patch('psycopg2.connect')
    def test_test_connection_success(self, mock_connect):
        """Test successful connection test"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)
        mock_connect.return_value = mock_conn
        
        client = VisionDBClient(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_password'
        )
        
        result = client.test_connection()
        
        assert result is True
        mock_cursor.execute.assert_called_once_with('SELECT 1')
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('psycopg2.connect')
    def test_test_connection_failure(self, mock_connect):
        """Test connection test failure"""
        mock_connect.side_effect = Exception("Connection failed")
        
        client = VisionDBClient(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_password'
        )
        
        result = client.test_connection()
        
        assert result is False
    
    @patch('psycopg2.connect')
    def test_get_allocations_success(self, mock_connect):
        """Test successful allocations retrieval"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock query result
        mock_cursor.fetchall.return_value = [
            (1, 28, 3302, 3842, 3189, '2025-03-01', '2026-01-31', 100, 0, None, 'consultant', 
             '2025-06-24 14:32:40.779113+00', '2025-06-24 14:32:40.779115+00', None, None)
        ]
        mock_cursor.description = [
            ('id',), ('simulation_id',), ('original_id',), ('employee_id',), ('project_id',),
            ('start_date',), ('end_date',), ('allocation_percent',), ('rate',), ('rate_type',),
            ('role',), ('created_at',), ('updated_at',), ('deleted_at',), ('promoted_at',)
        ]
        
        mock_connect.return_value = mock_conn
        
        client = VisionDBClient(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_password'
        )
        
        result = client.get_allocations()
        
        assert result is not None
        assert len(result) == 1
        assert result.iloc[0]['id'] == 1
        assert result.iloc[0]['employee_id'] == 3842
        assert result.iloc[0]['project_id'] == 3189
        assert result.iloc[0]['allocation_percent'] == 100
        
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('psycopg2.connect')
    def test_get_allocations_failure(self, mock_connect):
        """Test allocations retrieval failure"""
        mock_connect.side_effect = Exception("Query failed")
        
        client = VisionDBClient(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_password'
        )
        
        result = client.get_allocations()
        
        assert result is None
    
    @patch('psycopg2.connect')
    def test_get_clients_success(self, mock_connect):
        """Test successful clients retrieval"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock query result
        mock_cursor.fetchall.return_value = [
            (1, 'Test Client', 'CLI001', '2023-01-01 00:00:00+00', '2024-01-01 00:00:00+00')
        ]
        mock_cursor.description = [
            ('id',), ('name',), ('code',), ('created_at',), ('updated_at',)
        ]
        
        mock_connect.return_value = mock_conn
        
        client = VisionDBClient(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_password'
        )
        
        result = client.get_clients()
        
        assert result is not None
        assert len(result) == 1
        assert result.iloc[0]['id'] == 1
        assert result.iloc[0]['name'] == 'Test Client'
        assert result.iloc[0]['code'] == 'CLI001'
    
    @patch('psycopg2.connect')
    def test_get_employees_success(self, mock_connect):
        """Test successful employees retrieval"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock query result
        mock_cursor.fetchall.return_value = [
            (1, 'John Doe', 'john.doe@test.com', '2023-01-01 00:00:00+00', '2024-01-01 00:00:00+00')
        ]
        mock_cursor.description = [
            ('id',), ('name',), ('email',), ('created_at',), ('updated_at',)
        ]
        
        mock_connect.return_value = mock_conn
        
        client = VisionDBClient(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_password'
        )
        
        result = client.get_employees()
        
        assert result is not None
        assert len(result) == 1
        assert result.iloc[0]['id'] == 1
        assert result.iloc[0]['name'] == 'John Doe'
        assert result.iloc[0]['email'] == 'john.doe@test.com'
    
    @patch('psycopg2.connect')
    def test_get_projects_success(self, mock_connect):
        """Test successful projects retrieval"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock query result
        mock_cursor.fetchall.return_value = [
            (1, 'Test Project', 1, '2023-01-01 00:00:00+00', '2024-01-01 00:00:00+00')
        ]
        mock_cursor.description = [
            ('id',), ('name',), ('client_id',), ('created_at',), ('updated_at',)
        ]
        
        mock_connect.return_value = mock_conn
        
        client = VisionDBClient(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_password'
        )
        
        result = client.get_projects()
        
        assert result is not None
        assert len(result) == 1
        assert result.iloc[0]['id'] == 1
        assert result.iloc[0]['name'] == 'Test Project'
        assert result.iloc[0]['client_id'] == 1
    
    @patch('psycopg2.connect')
    def test_get_all_data_success(self, mock_connect):
        """Test successful retrieval of all data"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock different query results
        def mock_fetchall():
            if 'allocations' in str(mock_cursor.execute.call_args):
                return [(1, 28, 3302, 3842, 3189, '2025-03-01', '2026-01-31', 100, 0, None, 'consultant', 
                        '2025-06-24 14:32:40.779113+00', '2025-06-24 14:32:40.779115+00', None, None)]
            elif 'clients' in str(mock_cursor.execute.call_args):
                return [(1, 'Test Client', 'CLI001', '2023-01-01 00:00:00+00', '2024-01-01 00:00:00+00')]
            elif 'employees' in str(mock_cursor.execute.call_args):
                return [(1, 'John Doe', 'john.doe@test.com', '2023-01-01 00:00:00+00', '2024-01-01 00:00:00+00')]
            elif 'projects' in str(mock_cursor.execute.call_args):
                return [(1, 'Test Project', 1, '2023-01-01 00:00:00+00', '2024-01-01 00:00:00+00')]
            return []
        
        mock_cursor.fetchall.side_effect = mock_fetchall
        
        # Mock description for different queries
        def mock_description():
            if 'allocations' in str(mock_cursor.execute.call_args):
                return [('id',), ('simulation_id',), ('original_id',), ('employee_id',), ('project_id',),
                       ('start_date',), ('end_date',), ('allocation_percent',), ('rate',), ('rate_type',),
                       ('role',), ('created_at',), ('updated_at',), ('deleted_at',), ('promoted_at',)]
            else:
                return [('id',), ('name',), ('code',), ('created_at',), ('updated_at',)]
        
        mock_cursor.description = mock_description()
        
        mock_connect.return_value = mock_conn
        
        client = VisionDBClient(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_password'
        )
        
        result = client.get_all_data()
        
        assert result is not None
        assert 'allocations' in result
        assert 'clients' in result
        assert 'employees' in result
        assert 'projects' in result
        
        assert len(result['allocations']) == 1
        assert len(result['clients']) == 1
        assert len(result['employees']) == 1
        assert len(result['projects']) == 1
    
    @patch('psycopg2.connect')
    def test_get_all_data_partial_failure(self, mock_connect):
        """Test all data retrieval with partial failure"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock successful allocations query
        def mock_fetchall():
            if 'allocations' in str(mock_cursor.execute.call_args):
                return [(1, 28, 3302, 3842, 3189, '2025-03-01', '2026-01-31', 100, 0, None, 'consultant', 
                        '2025-06-24 14:32:40.779113+00', '2025-06-24 14:32:40.779115+00', None, None)]
            elif 'clients' in str(mock_cursor.execute.call_args):
                raise Exception("Clients query failed")
            return []
        
        mock_cursor.fetchall.side_effect = mock_fetchall
        mock_cursor.description = [('id',), ('simulation_id',), ('original_id',), ('employee_id',), ('project_id',),
                                  ('start_date',), ('end_date',), ('allocation_percent',), ('rate',), ('rate_type',),
                                  ('role',), ('created_at',), ('updated_at',), ('deleted_at',), ('promoted_at',)]
        
        mock_connect.return_value = mock_conn
        
        client = VisionDBClient(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_password'
        )
        
        result = client.get_all_data()
        
        assert result is not None
        assert 'allocations' in result
        assert 'clients' in result
        assert 'employees' in result
        assert 'projects' in result
        
        # Allocations should be successful
        assert len(result['allocations']) == 1
        # Other tables should be empty due to failure
        assert len(result['clients']) == 0
        assert len(result['employees']) == 0
        assert len(result['projects']) == 0
    
    def test_connection_params_validation(self):
        """Test connection parameters validation"""
        # Test with valid parameters
        client = VisionDBClient(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_password'
        )
        
        assert client.connection_params['host'] == 'localhost'
        assert client.connection_params['port'] == 5432
        assert client.connection_params['database'] == 'test_db'
        assert client.connection_params['user'] == 'test_user'
        assert client.connection_params['password'] == 'test_password'
    
    @patch('psycopg2.connect')
    def test_context_manager_cleanup(self, mock_connect):
        """Test that context manager properly cleans up resources"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        client = VisionDBClient(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_password'
        )
        
        with client.get_connection() as conn:
            pass
        
        # Verify cleanup was called
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
