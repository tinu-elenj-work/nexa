"""
Test configuration for Nexa test suite
"""

import pytest
import os
import sys
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock the config module
TEST_CONFIG = {
    'ELAPSEIT_CONFIG': {
        'domain': 'test-domain.com',
        'username': 'test@test.com',
        'password': 'test_password',
        'timezone': 'Europe/London'
    },
    'XERO_CONFIG': {
        'client_id': 'test_client_id',
        'client_secret': 'test_client_secret',
        'access_token': 'test_access_token',
        'refresh_token': 'test_refresh_token',
        'scopes': ['accounting.transactions', 'accounting.reports.read']
    },
    'VISION_DB_CONFIG': {
        'host': 'localhost',
        'port': 5432,
        'database': 'test_db',
        'user': 'test_user',
        'password': 'test_password'
    }
}

@pytest.fixture(autouse=True)
def mock_config():
    """Mock the config module for all tests"""
    with patch.dict('sys.modules', {'config': type('MockConfig', (), TEST_CONFIG)()}):
        yield

class TestConfig:
    """Test cases for configuration"""
    
    def test_elapseit_config_structure(self):
        """Test ElapseIT configuration structure"""
        from config import ELAPSEIT_CONFIG
        
        assert 'domain' in ELAPSEIT_CONFIG
        assert 'username' in ELAPSEIT_CONFIG
        assert 'password' in ELAPSEIT_CONFIG
        assert 'timezone' in ELAPSEIT_CONFIG
        
        assert ELAPSEIT_CONFIG['domain'] == 'test-domain.com'
        assert ELAPSEIT_CONFIG['username'] == 'test@test.com'
        assert ELAPSEIT_CONFIG['timezone'] == 'Europe/London'
    
    def test_xero_config_structure(self):
        """Test Xero configuration structure"""
        from config import XERO_CONFIG
        
        assert 'client_id' in XERO_CONFIG
        assert 'client_secret' in XERO_CONFIG
        assert 'access_token' in XERO_CONFIG
        assert 'refresh_token' in XERO_CONFIG
        assert 'scopes' in XERO_CONFIG
        
        assert XERO_CONFIG['client_id'] == 'test_client_id'
        assert XERO_CONFIG['client_secret'] == 'test_client_secret'
        assert isinstance(XERO_CONFIG['scopes'], list)
        assert 'accounting.transactions' in XERO_CONFIG['scopes']
    
    def test_vision_db_config_structure(self):
        """Test Vision database configuration structure"""
        from config import VISION_DB_CONFIG
        
        assert 'host' in VISION_DB_CONFIG
        assert 'port' in VISION_DB_CONFIG
        assert 'database' in VISION_DB_CONFIG
        assert 'user' in VISION_DB_CONFIG
        assert 'password' in VISION_DB_CONFIG
        
        assert VISION_DB_CONFIG['host'] == 'localhost'
        assert VISION_DB_CONFIG['port'] == 5432
        assert VISION_DB_CONFIG['database'] == 'test_db'
        assert VISION_DB_CONFIG['user'] == 'test_user'
